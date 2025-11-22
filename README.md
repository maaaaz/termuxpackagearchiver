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
usage: termuxpackagearchiver.py [-h] -d DIRECTORY [-p PREFIX]

version: 1.0

optional arguments:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory DIRECTORY
                        Directory containing directories of package
  -p PREFIX, --prefix PREFIX
                        Prefix to use for archive.org items (default: "termux_pkg_archive_")
```
  

Changelog
---------
* version 1.0 - 2025-11-11: Publication on pypi.org


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