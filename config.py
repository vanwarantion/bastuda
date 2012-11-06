#!/usr/bin/python
# -*- coding: utf-8 -*-

# Backup items:
items = {
    'code': {
        'src': ["/home/koray/Dropbox/code"],
        'dst': [
            {'path': "/var/VMs/backups", "increments": 3},
        ],
        'rsyncOptions': ['--cvs-exclude'],
        'excludes': ['.pyc$']
    },
}

# Backup configuration:
settings = {
    'tmp': "/tmp",
    'excludes': [
        '~$',
        '/home/[^/]+?/\.gvfs/',
        '/home/[^/]+?/\..+/[cC]ache/',
        '/home/[^/]+?/\..+/[tT]rash/',
        '/home/[^/]+?/\.thumbnails/',
        '.mpeg$',
        '.mkv$',
        '.iso$',
    ],
    'rsyncOptions': ['-rptgoD', '--delete', '--safe-links'],
    'logLevel': 0,                          # 0: debug, 1: info, 2: warning, 3: error, 4: critical
}

# rsync output fields:
parts = {
    'perm': (0, 10),
    'size': (11, 22),
    'date': (23, 33),
    'time': (34, 42),
    'path': (43, -1),
}
