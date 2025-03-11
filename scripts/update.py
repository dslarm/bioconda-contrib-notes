#!/usr/bin/python

import os
import matplotlib.pyplot as plt

MAX_PLOTS=200
MAA=14

os.system("git clone https://github.com/bioconda/bioconda-stats")
os.chdir("bioconda-stats")
os.system("git checkout data")


filename="package-downloads/anaconda.org/bioconda/channel.tsv"

with open(filename, 'r') as f:
    line = f.readline()
    fields = line.rstrip().split('\t')
    data = {field : [] for field in fields}
    for line in f:
        entries = line.split('\t')

        for i in range(0,len(fields)):
            if len(entries) > i:
                if fields[i] != 'date':
                    data[fields[i]].append(float(entries[i].rstrip()) if entries[i].rstrip() != '' else 0)
                else:
                    data[fields[i]].append(entries[i])


    for field in fields:
        if field != 'date':
            data[f'{field}_MA{MAA}'] = [0] * MAA
        else:
            data[f'{field}_MA{MAA}'] = data['date'][0:MAA]

        for i in range(0, len(data[field]) - MAA):
            if field != 'date':
                data[f'{field}_MA{MAA}'].append((data[field][i+MAA] - data[field][i])/MAA)
            else:
                data[f'{field}_MA{MAA}'].append(data[field])


    for field in ['osx-arm64', 'linux-aarch64', 'linux-64', 'osx-64', 'noarch']:
        plt.plot(range(0, len(data['date']))[-MAX_PLOTS:], data[f'{field}_MA{MAA}'][-MAX_PLOTS:])
    plt.savefig('../downloads.png')
