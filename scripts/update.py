#!/usr/bin/python

import os.system

os.system("git clone https://github.com/bioconda/bioconda-stats")
os.system("cd bioconda-stats")
os.system("git checkout data")


filename="package-downloads/anaconda.org/bioconda/channel.tsv"

with open(filename, 'r') as f:
    while line = f.readline():
        print (line)


