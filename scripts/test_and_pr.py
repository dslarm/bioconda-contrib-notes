#!env python3
import subprocess
import sys
import re
import os

for i in sys.argv[1:]:
    os.environ['OSX_TOO'] = "1"
    subprocess.run(['git', 'pull'])
    r = subprocess.run(['python3', '../bioconda-contrib-notes/scripts/bioconda_fix.py', i])
    suffix = '-osx-arm64'
    r = subprocess.run(['git', 'checkout', i + suffix])
    phname = f'{i}: add osx-arm64'
    if r.returncode:
        phname =  phname = f'{i}: add linux-aarch64, osx-arm64'
        suffix = '-aarch64'
        r = subprocess.run(['git', 'checkout', i + suffix])
    if r.returncode:
        continue
            
    r = subprocess.run(['bioconda-utils','build', '--packages', i])
    if not r.returncode:
        r = subprocess.run(['gh', 'pr', 'create', '--title', phname, '--body', ''])
    else:
        print(f'ERROR: {i}')
    subprocess.run(['git', 'checkout', 'master'])
    subprocess.run(['git', 'pull'])
