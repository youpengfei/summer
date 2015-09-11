#!/usr/bin/python

import os, subprocess

subprocess.call(['virtualenv', 'summer'])
subprocess.call([os.path.join('summer', 'bin', 'pip'), 'install', '-r', 'requirements.txt'])
