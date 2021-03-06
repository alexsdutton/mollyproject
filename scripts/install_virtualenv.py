#!/usr/bin/env python

import os, sys, os.path, subprocess, shutil, traceback

def copy_demos(source_path, deploy_path):
    # Copy the demos across
    shutil.copytree(
        os.path.join(source_path, 'demos'),
        os.path.join(deploy_path, 'demos'),
    )

def main(source_path, deploy_path):
    if os.path.exists(deploy_path):
        print "Cannot deploy to path - already exists"
        return 1

    commands = [
        ('Creating', 'virtual environment', ["virtualenv", "--distribute", "--no-site-packages", deploy_path]),
    ]

    requirements = [l[:-1] for l in open(os.path.join(source_path, "requirements", "core.txt")) if l[:-1]]

    for requirement in requirements:
        commands.append(
            ('Installing', requirement,
             [os.path.join(deploy_path, "bin", "pip"), "install", "-U", requirement])
        )

    commands += [
        ('Deploying', 'molly',
         [os.path.join(deploy_path, "bin", "python"), os.path.join(source_path, "setup.py"), "install"]),
        ('Copying', 'demos', copy_demos),
    ]

    stdout_log = open('molly.stdout.log', 'w')
    stderr_log = open('molly.stderr.log', 'w')
    succeeded = True
    for i, (action, item, command) in enumerate(commands):
        print "%s %s (%2d/%2d)" % (action[:12].ljust(12), item[:40].ljust(40), (i+1), len(commands)),
        if callable(command):
            try:
                return_code = command(source_path, deploy_path) or 0
            except Exception, e:
                return_code = 1
                traceback.print_exc(file=stderr_log)
        else:
            try:
                return_code = subprocess.call(command, stdout=stdout_log, stderr=stderr_log)
            except OSError, e:
                print "\n", ("No such shell command: %r" % command[0]).ljust(61),
                return_code = 1
        print "[%s]" % ('FAILED' if return_code else '  OK  ')
        succeeded = succeeded and (return_code == 0)

    if succeeded:
        print """
Molly was successfully installed to %(deploy_path)s.
The following command will take you inside your virtualenv:

$ source %(activate)s""" % {
            'deploy_path': deploy_path,
            'activate': os.path.join(deploy_path, "bin", "activate"),
        }
    else:
        print """
The installation failed. You may find useful information in molly.stdout.log
and molly.stderr.log. For assistance, please e-mail the mailing list at
mollyproject-devel@lists.sourceforge.net or join the #molly IRC channel on
irc.freenode.net.""" 


if __name__ == '__main__':
    source_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    deploy_path = os.path.abspath(sys.argv[1])
    exit(main(source_path, deploy_path) or 0)
