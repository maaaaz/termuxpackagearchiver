termuxpackagearchiver
=====================

Description
-----------
A simple script to archive Termux packages on archive.org


Usage
-----
```
$ pip install termuxpackagearchiver

# first, configure your archive.org credentials
$ ia configure 

$ termuxpackagearchiver
usage: termuxpackagearchiver [-h] -a {upload,parse_commits} [-d DIRECTORY]
                             [-p PREFIX] [-s] [-i INPUT_COMMIT_FILE]
                             [-o OUTPUT_DIRECTORY]

version: 1.4

options:
  -h, --help            show this help message and exit

Action parameters:
  -a, --action {upload,parse_commits}
                        Action to perform (upload, parse_commits)

Upload parameters:
  -d, --directory DIRECTORY
                        Directory containing directories of package
  -p, --prefix PREFIX   Prefix to use for archive.org items (default:
                        "termux_pkgs_archive_")
  -s, --skip-file-check-items
                        Skip file existence on archive.org items (default:
                        False)

Parse parameters:
  -i, --input-commit-file INPUT_COMMIT_FILE
                        Input commit log file to parse
  -o, --output-directory OUTPUT_DIRECTORY
                        Output directory for downloaded files
```
  
  

Copyright and license
---------------------
I am neither affiliated with the Internet Archive project, nor the Termux one.

termuxpackagearchiver is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

termuxpackagearchiver is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  

See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU General Public License along with termuxpackagearchiver. 
If not, see http://www.gnu.org/licenses/.

Contact
-------
* Thomas Debize < tdebize at mail d0t com >