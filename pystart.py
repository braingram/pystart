#!/usr/bin/env python

import argparse
import glob
import os
import urllib2

setup_url = "http://braingram.github.com/simple_setup/setup.py"
bang_splat = "#!/usr/bin/env python"
default_script = """\
import logging


def main():
    pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
"""


def make_init(directory):
    init_fn = os.path.join(directory, '__init__.py')
    # find all .py files in directory
    pyfiles = glob.glob(os.path.join(directory, '*.py'))
    if len(pyfiles) == 0:
        make_script(os.path.join(directory, 'main.py'))
        pyfiles = ['main.py']
    with open(init_fn, 'w') as init_file:
        init_file.write("%s\n" % bang_splat)
        all_str = "__all__ = ["
        for pyf in pyfiles:
            fn = os.path.splitext(os.path.basename(pyf))[0]
            init_file.write("import %s\n" % fn)
            all_str += "'%s', " % fn
        all_str += "]\n"
        init_file.write("\n")
        init_file.write(all_str)


def make_module(name):
    if os.path.exists(name):
        if os.path.isdir(name):
            # make this directory into a module
            init_fn = os.path.join(name, '__init__.py')
            if os.path.exists(init_fn):
                print "Directory [%s] is already a module" % \
                        name
                return
            make_init(name)
        else:
            # make this file into a module
            print "A file already exists named %s" % name
            return
    else:
        # make new directory and turn it into a module
        os.makedirs(name)
        make_init(name)


def make_project(name):
    # make directory
    if not os.path.exists(name):
        os.makedirs(name)
    elif not os.path.isdir(name):
        print "A file already exists named %s" % name
        return

    # add setup.py
    setup_fn = os.path.join(name, 'setup.py')
    if not os.path.exists(setup_fn):
        try:
            r = urllib2.urlopen(setup_url)
            with open(setup_fn, 'w') as setup_file:
                setup_file.write(r.read())
        except:
            print "Failed to fetch setup.py from %s" % setup_url

    # add requirements.txt
    reqs_fn = os.path.join(name, 'requirements.txt')
    if not os.path.exists(reqs_fn):
        with open(reqs_fn, 'w') as reqs_file:
            reqs_file.write("")  # nothing for now

    # make module
    module_path = os.path.join(name, name)
    make_module(module_path)


def make_script(name):
    if not (os.path.splitext(name)[1].lower() == '.py'):
        name += '.py'
    if os.path.exists(name):
        print "A file already exists named %s" % name
        return
    with open(name, 'w') as f:
        f.write("%s\n" % bang_splat)
        f.write(default_script)


actions = { \
        'module': make_module,
        'm': make_module,
        'project': make_project,
        'p': make_project,
        'script': make_script,
        's': make_script,
        }

parser = argparse.ArgumentParser(description='Make a python thing')
parser.add_argument('thing', metavar='thing', type=str,
        help='the thing to make')
parser.add_argument('args', metavar='args', type=str, nargs='*',
        help='arguments to make the thing', default=[])
args = parser.parse_args()

if args.thing in actions.keys():
    actions[args.thing](*args.args)
