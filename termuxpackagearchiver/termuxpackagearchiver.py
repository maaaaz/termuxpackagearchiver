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
VERSION = '1.0'
PREFIX = 'termux_pkg_archive_'

# For testing purposes
#PREFIX = 'test_termux_pkg_archive_'

# Options definition
parser = argparse.ArgumentParser(description="version: " + VERSION)
parser.add_argument('-d', '--directory', help='Directory containing directories of package', required = True)
parser.add_argument('-p', '--prefix', help='Prefix to use for archive.org items (default: "%s")' % PREFIX, default = PREFIX)

ALPHABET_ALPHANUM = list(string.ascii_lowercase + string.digits)
ALPHABET = list(['lib' + i for i in ALPHABET_ALPHANUM]) + ALPHABET_ALPHANUM

def upload_files(dirs_to_upload, archive_items_to_list, archive_items_file_list, options):
    for dir_to_upload in dirs_to_upload:
        for file_to_upload in glob.iglob(os.path.join(dir_to_upload, '*.deb'), recursive=True):
            file_to_upload_filename = os.path.basename(file_to_upload)
            
            if not(file_to_upload_filename in archive_items_file_list):
                archive_item_name = find_matching_archive_item_bin(dir_to_upload.name, options)
                relative_file_path = os.path.join(os.path.basename(os.path.dirname(file_to_upload)), os.path.basename(file_to_upload))
                
                print('[+] Uploading "%s" to archive.org item "%s"' % (relative_file_path, archive_item_name))
                try:
                    upload_result = sh.ia('upload', '-n', '-v', '--no-backup', '--keep-directories', "%s" % archive_item_name, "%s" % relative_file_path, _cwd=options.directory)
                    print(upload_result)
                
                except sh.ErrorReturnCode as e:
                    print('[!] Error while uploading "%s" to "%s":\n"%s"' % (relative_file_path, archive_item_name, e))
                
    return None

def list_archive_items(archive_items_to_list, options):
    file_list = []
    for archive_item_name in archive_items_to_list:
        current_file_list = None
        try:
            #current_file_list = sh.ia('list', "termux_pkg_archive_test", '-g', '*.deb' )
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
    uniq_pkg_pattern_bins = []
    
    for elem in dirs_to_upload:
        pkg_pattern_bin = find_matching_pkg_bin_pattern(elem.name, options)
        if not(pkg_pattern_bin in uniq_pkg_pattern_bins):
            uniq_pkg_pattern_bins.append(pkg_pattern_bin)
    
    for found_pkg_pattern_bin in uniq_pkg_pattern_bins:
        archive_item_name = options.prefix + found_pkg_pattern_bin
        archive_items_to_list.append(archive_item_name)
    
    return archive_items_to_list

def walk_dir(options):
    dirs_to_upload = []
    
    root_directory = os.path.abspath(options.directory)
    if os.path.isdir(root_directory):
        print('[+] Directory to process:"%s"' % root_directory)
        for elem in os.scandir(root_directory):
            directory = None
            if elem.is_dir():
                directory = elem
                if glob.glob(os.path.join(directory, '*.deb'), recursive=True):
                    print('[+] Found .deb files in: "%s"' % directory.path)
                    dirs_to_upload.append(directory)
    
    else:
        print('\n[!] Directory "%s" can not be found or is not a directory !' % directory)
    
    return dirs_to_upload

def main():
    global parser
    options = parser.parse_args()
    
    dirs_to_upload = walk_dir(options)
    #print(dirs_to_upload)
    
    archive_items_to_list = enumerate_archive_items_to_list(dirs_to_upload, options)
    #print(archive_items_to_list)
    
    archive_items_file_list = list_archive_items(archive_items_to_list, options)
    #print(archive_items_file_list)
    
    upload_files(dirs_to_upload, archive_items_to_list, archive_items_file_list, options)
    
    return None

if __name__ == "__main__" :
    main()