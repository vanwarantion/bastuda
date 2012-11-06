bastuda
=======

Backup Stuff Daily

This is a basic script I use for the nightly backup of my personal codebase.

There are a couple simple settings to change before using bastuda:
===

config.py file:

Normally, there is nothing here to edit except the "items" section.

Backup items are listed in a python dict where every key is a backup item. In the default version, 'code' is the only backup source.

Multiple source paths can be given in the 'src' array. Be careful here and don't add any trailing slashes ('/') at the end of a path.
Bastuda will backup each path in the source array to the each location given in the 'dst' (target paths) items.

With every destination, a number CAN be given to determine incremental copies. Those copies will then be rotated during the backup operation.

Default parameters for the rsync command are listed in the settings['rsyncOptions'] array. However, extra options for each backup item can be defined.
For example, "--cvs-exclude" is in the default config file as I am normally using this option to backup data which consist of mostly source code files.

You can also make exclusions to the standard backup operation. By default, I have copied some patterns to be excluded from the default profile of the sbackup (http://sourceforge.net/projects/sbackup/develop).
