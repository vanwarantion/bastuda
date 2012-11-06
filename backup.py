#!/usr/bin/python
# -*- coding: utf-8 -*-

# Koray Kalmaz - 2012
# kalmaz@gmail.com

# Backup Stuff Daily
# Run rsync for listed paths

productName = 'bastuda'

# imports:
import config, os, subprocess, shlex, datetime, logging, logging.handlers, tempfile, shutil

# rsync command:
command = 'rsync'

# get logging:
my_logger = logging.getLogger(productName)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
my_logger.addHandler(handler)
logLevels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
logCmd = [my_logger.debug, my_logger.info, my_logger.warning, my_logger.error, my_logger.critical]

def bkTar(itemName, s, n, d, opts = []):
    # tar backup
    msg('Backing up %s to %s/%s-%s.tar' % (itemName, d, itemName, dateString()), 1)


def bkRsync(itemName, s, n, d, opts = []):
    rv = 0
    # rsync backup
    dstr = dateString()
    fname = '%s-%s' % (itemName, dstr)
    s = s[0:s.rfind('/')]
    fpath = tempfile.gettempdir() + '/%s.list' % fname
    msg("Creating tmpfile %s" % fpath, 1)
    f = open(fpath, 'w')
    for i in n:
        f.write("%s\n" % (i['path']))
    f.close()
    # opts.append('-v')
    cmdopts = paramList(opts)
    target = "%s/%s-current" % (d, itemName)
    msg("Execute: %s %s --files-from=%s %s %s" % (command, cmdopts, fpath, s, target), 1)
    try:
        p = subprocess.check_call((command, '-a', '--delete', '-v', '--files-from=%s' % fpath, s, target))
    except Exception as e:
        msg("Backup Error: %s" % str(e), 3)
        rv = 1
    os.remove(fpath)
    return rv

def dateString():
    x = datetime.datetime.now()
    d = '%04d-%02d-%02d' % (int(x.year), int(x.month), int(x.day))
    t = '%02d%02d' % (int(x.hour), int(x.minute))
    return '%s-%s' % (d, t)

def freeSpace(n = '/'):
    # Find free space on target drive:
    s = os.statvfs(config.settings['tmp'])
    rv = s.f_bavail * s.f_frsize
    return rv

def paramList(n, compareWith = None, delimiter = ' '):
    # Returns single line parameters:
    rv = ''
    if compareWith:
        # merge:
        for i in compareWith:
            if i not in n:
                n.append(i)
    for i in n:
        rv = rv + delimiter + i
    return rv

def getListR(s, d, rsyncOptions):
    # Returns the list of items to be rsynced (s: source, d: destination)
    rv = []
    # Default options:
    cmd = command
    opts = paramList(rsyncOptions)
    cmd = '%s %s --list-only "%s" "%s"' % (cmd, opts, s, d)
    msg('Executing: %s' % str(shlex.split(cmd)), 1)
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    totalSize = 0
    while(True):
        retcode = p.poll() #returns None while subprocess is running
        line = p.stdout.readline()
        lfields = {}
        for i in config.parts.keys():
            stbegin = int(config.parts[i][0])
            stend = int(config.parts[i][1])
            lfields[i] = line[stbegin : stend].strip()
        lfields['line'] = line
        totalSize = totalSize + int(lfields['size'])
        rv.append(lfields)
        if(retcode is not None):
            break
    msg("Total %s files, size: %s" % (str(len(rv)), str(totalSize)), 1)
    # TODO: Check free disk space on target path
    return rv

def msg(msg, level):
    if config.settings['logLevel'] <= level:
        print "%s[%s]:\t%s" % (productName, str(os.getpid()), msg)
        logCmd[level]("%s[%s]:\t%s" % (productName, str(os.getpid()), msg))

if __name__ == "__main__":
    my_logger.setLevel(logLevels[config.settings['logLevel']])
    # TODO: HERE: read config, write config
    t0 = datetime.datetime.now()    # Start time
    for i in config.items.keys():
        msg("Backing up item: %s" % str(i), 1)
        for s in config.items[i]['src']:
            # Get the list of files
            msg("Source path: %s" % s, 1)
            if 'rsyncOptions' in config.items[i].keys():
                # private rsync options, merge:
                for o in config.settings['rsyncOptions']:
                    if o not in config.items[i]['rsyncOptions']:
                        config.items[i]['rsyncOptions'].append(o)
            if 'excludes' not in config.items[i].keys():
                config.items[i]['excludes'] = []
            for e in config.settings['excludes']:
                config.items[i]['excludes'].append(e)
            excl = ''
            for e in config.items[i]['excludes']:
                excl = excl + """ --exclude='%s'""" % e
            config.items[i]['rsyncOptions'].append(excl)
            target = "%s/%s-current" % (config.items[i]['dst'][0]['path'], i)
            syncList = getListR(s, target, config.items[i]['rsyncOptions'])
            # print "Total %s items" % len(syncList)
            # backup types x function references (do not touch this):
            bkDefs = {'rsync': bkRsync, 'tar': bkTar}
            for t in config.items[i]['dst']:
                # Rotate old copies:
                if "increments" in t.keys():
                    for inc in range(t["increments"], 1, -1):
                        incB = "%s/%s-%d" % (config.items[i]['dst'][0]['path'], i, inc)
                        incA = "%s/%s-%d" % (config.items[i]['dst'][0]['path'], i, inc - 1)
                        if os.path.exists(incB):
                            msg('Removing copy %d' % inc, 1)
                            shutil.rmtree(incB)
                        if os.path.exists(incA):
                            msg("Rotate copy %d to %d" % (inc -1, inc), 1)
                            os.rename(incA, incB)
                    try:
                        incA
                    except NameError:
                        msg("No rotation is defined", 1)
                    else:
                        # current to 1
                        msg("Copy current to %s" % incA, 1)
                        shutil.copytree(target, incA)
                # Create target folder
                msg("Target: %s" % t['path'], 1)
                r = bkRsync(i, s, syncList, t['path'], config.settings['rsyncOptions'])
                msg("rsync operation has returned %d" % r, 2)
        msg('Item: "%s" is done' % i, 1)
    t1 = datetime.datetime.now()    # Finish time
    msg("Backup Completed. Total time: %s" % str(t1 - t0), 1)
