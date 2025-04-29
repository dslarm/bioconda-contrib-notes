#!env python3
import subprocess
import sys
import re
import os

for i in sys.argv[1:]:

    osx = 'OSX_TOO' in os.environ
    
    if osx:
        suffix = '-osx-arm64'
        phname = f'{i}: add osx-arm64'
    else:
        suffix = '-aarch64'
        phname = f'{i}: add linux-aarch64'

    subprocess.run(['git', 'pull'])
    r = subprocess.run(['python3', '../bioconda-contrib-notes/scripts/bioconda_fix.py', i])
    r = subprocess.run(['git', 'checkout', i + suffix])

    if r.returncode and osx:
        suffix = '-aarch64'
        r = subprocess.run(['git', 'checkout', i + suffix])
        phname = f'{i}: add linux-aarch64, osx-arm64'

    if r.returncode:
        continue
            
    if sys.platform is 'linux':
        r = subprocess.run(['bioconda-utils', 'build', '--docker', '--mulled-test','--docker-base-image quay.io/bioconda/bioconda-utils-build-env-cos7-aarch64:3.3.2','--packages', i])
    else:
        r = subprocess.run(['bioconda-utils','build', '--packages', i])
    if not r.returncode:
        r = subprocess.run(['gh', 'pr', 'create', '--title', phname, '--body', ''])
    else:
        print(f'ERROR: {i}')
    subprocess.run(['git', 'checkout', 'master'])
    subprocess.run(['git', 'pull'])
