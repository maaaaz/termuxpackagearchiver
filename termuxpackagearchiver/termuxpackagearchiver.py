#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import argparse
import string
import time
import glob
import pprint

import sh

# Globals
VERSION = '1.6'
ACTION_CHOICES = ['upload', 'parse_commits']
PREFIX = 'termux_pkgs_archive_'

ALPHABET_ALPHANUM = list(string.ascii_lowercase + string.digits)
ALPHABET = list(['lib' + i for i in ALPHABET_ALPHANUM]) + ALPHABET_ALPHANUM


# Options definition
parser = argparse.ArgumentParser(description="version: " + VERSION)
action_grp = parser.add_argument_group('Action parameters')
action_grp.add_argument('-a', '--action', help='Action to perform (%s)' % ", ".join(ACTION_CHOICES), choices = ACTION_CHOICES, type=str.lower, required = True)

upload_grp = parser.add_argument_group('Upload parameters')
upload_grp.add_argument('-d', '--directory', help='Directory containing directories of package')
upload_grp.add_argument('-p', '--prefix', help='Prefix to use for archive.org items (default: "%s")' % PREFIX, default = PREFIX)
upload_grp.add_argument('-s', '--skip-file-check-items', help='Skip file existence on archive.org items (default: False)', action = 'store_true', default = False)

parse_grp = parser.add_argument_group('Parse_commits parameters')
parse_grp.add_argument('-i', '--input-commit-file', help='Input commit log file to parse')
parse_grp.add_argument('-o', '--output-directory', help='Output directory for downloaded files')


def get_download_url(repo, pkg, options):
    result = ''
    
    repositories_mapping = { 
        'root':  'https://packages.termux.dev/apt/termux-root/pool/stable/',
        'x11':   'https://packages.termux.dev/apt/termux-x11/pool/main/',
        'main':  'https://packages.termux.dev/apt/termux-main/pool/main/',
        'glibc': 'https://packages.termux.dev/apt/termux-glibc/pool/stable/'
    }
    
    bin_pattern = find_matching_pkg_bin_pattern(pkg, options)
    if bin_pattern and (repo in repositories_mapping.keys()):
        # important to end with a trailing slash for wget to understand that it should mirror
        result = "%s%s/%s/" % (repositories_mapping[repo], bin_pattern, pkg)
    
    return result

def parse_and_download(options):
    p_parse = re.compile(r'^(?P<commit_type>bump|rebuild|dwnpkg|addpkg|revbump|fix)\((?P<repo>.*)\/(?P<pkg>.*?)\)')
    
    with open(options.input_commit_file, mode='r', encoding='utf-8') as fd_input:
        for line in fd_input:
            parsing = p_parse.search(line)
            if parsing:
                repository = parsing.group('repo').lower()
                package_name = parsing.group('pkg')
                output_dir = os.path.abspath(os.path.join(options.output_directory, package_name))
                download_url = get_download_url(repository, package_name, options)
                if download_url:
                    print('[+] Downloading "%s" to "%s"' % (download_url, output_dir))
                    try:
                        sh.wget('--directory-prefix', '%s' % output_dir, '-e', 'robots=off', '--accept', '.deb', '-nv', '-i', '%s' % download_url)
                    except sh.ErrorReturnCode as e:
                        print('[!] Error while downloading "%s" to "%s":\n"%s"' % (download_url, output_dir, e))
                
                elif not(download_url):
                    print('[!] Error while constructing the download URL from this line "%s"' % line)        
    
    return None

def upload_files(dirs_to_upload, archive_items_to_list, archive_items_file_list, options):
    for dir_to_upload in dirs_to_upload:
        for file_to_upload in sorted(glob.iglob(os.path.join(dir_to_upload, '*.deb'), recursive=True)):
            file_to_upload_filename = os.path.basename(file_to_upload)
            
            if not(file_to_upload_filename in archive_items_file_list):
                archive_item_name = find_matching_archive_item_bin(dir_to_upload.name, options)
                relative_file_path = os.path.join(os.path.basename(os.path.dirname(file_to_upload)), os.path.basename(file_to_upload))
                
                print('[+] Uploading "%s" to archive.org item "%s"' % (relative_file_path, archive_item_name))
                try:
                    upload_result = sh.ia('upload', '-n', '-v', '--no-backup', '--keep-directories', "%s" % archive_item_name, "%s" % relative_file_path, _cwd=os.path.abspath(options.directory))
                    if upload_result:
                        print(upload_result)
                
                except sh.ErrorReturnCode as e:
                    print('[!] Error while uploading "%s" to "%s":\n"%s"' % (relative_file_path, archive_item_name, e))
                
    return None

def list_archive_items(archive_items_to_list, options):
    file_list = []
    if not(options.skip_file_check_items):
        for archive_item_name in archive_items_to_list:
            current_file_list = None
            try:
                current_file_list = sh.ia('list', "%s" % archive_item_name, '-g', '*.deb' )
            
            except sh.ErrorReturnCode as e:
                print('[!] Error while listing "%s":\n"%s"' % (archive_item_name, e))
            
            if current_file_list:
                data = current_file_list.splitlines()
                for current_file in data:
                    current_file = os.path.basename(current_file)
                    file_list.append(current_file)
    
    return file_list

def find_matching_pkg_bin_pattern(entry, options):
    result = None
    for pattern in ALPHABET:
        #print("tested pattern %s | entry %s" % (pattern,entry))
        if entry.startswith(pattern):
            result = pattern
            break
            
    return result

def find_matching_archive_item_bin(entry, options):
    archive_item_name = None
    found_pkg_pattern_bin = find_matching_pkg_bin_pattern(entry, options)
    if found_pkg_pattern_bin:
        archive_item_name = options.prefix + found_pkg_pattern_bin
    
    return archive_item_name

def enumerate_archive_items_to_list(dirs_to_upload, options):
    archive_items_to_list = []
    if not(options.skip_file_check_items):
        for elem in dirs_to_upload:
            archive_item_name = find_matching_archive_item_bin(elem.name, options)
            if not(archive_item_name in archive_items_to_list):
                archive_items_to_list.append(archive_item_name)
    
    return archive_items_to_list

def walk_dir(options):
    dirs_to_upload = []
    
    root_directory = os.path.abspath(options.directory)
    if os.path.isdir(root_directory):
        print('[+] Directory to process:"%s"' % root_directory)
        for elem in sorted(os.scandir(root_directory), key=lambda e: e.name):
            directory = None
            if elem.is_dir():
                directory = elem
                if glob.glob(os.path.join(directory, '*.deb'), recursive=True):
                    print('[+] Found .deb files in: "%s"' % directory.path)
                    dirs_to_upload.append(directory)
    
    else:
        print('\n[!] Directory "%s" can not be found or is not a directory !' % root_directory)
    
    return dirs_to_upload

def main():
    global parser
    options = parser.parse_args()
    
    if options.action == 'upload':
        if not(options.directory):
            parser.error('[!] UPLOAD action: please specify an input directory to upload')
            
        dirs_to_upload = walk_dir(options)
        archive_items_to_list = enumerate_archive_items_to_list(dirs_to_upload, options)
        archive_items_file_list = list_archive_items(archive_items_to_list, options)
        upload_files(dirs_to_upload, archive_items_to_list, archive_items_file_list, options)
        
    elif options.action == 'parse_commits':
        if not(options.input_commit_file):
            parser.error('[!] PARSE action: please specify an input commit log file to parse')
        
        if not(options.output_directory):
            parser.error('[!] PARSE action: please specify an output directory to download packages')
        
        parse_and_download(options)
        
    
    return None

if __name__ == "__main__" :
    main()