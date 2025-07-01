#!/usr/bin/python

import os
import matplotlib.pyplot as plt

MAX_PLOTS=200
MAA=14

os.system("git clone https://github.com/bioconda/bioconda-stats")
os.chdir("bioconda-stats")
os.system("git checkout data")


filename="package-downloads/anaconda.org/bioconda/channel.tsv"
packages = "package-downloads/anaconda.org/bioconda/platforms"
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
            data[f'{field}_MA{MAA}_percent'] = [0] * MAA
        else:
            data[f'{field}_MA{MAA}'] = data['date'][0:MAA]

        for i in range(0, len(data[field]) - MAA):
            if field != 'date':
                data[f'{field}_MA{MAA}'].append((data[field][i+MAA] - data[field][i])/MAA)
                data[f'{field}_MA{MAA}_percent'].append(data[f'{field}_MA{MAA}'][-1] / ((data['total'][i+MAA] - data['total'][i])/MAA)*100.0)
            else:
                data[f'{field}_MA{MAA}'].append(data[field])

    plt.suptitle(f"Daily downloads")
    plt.title(f'{MAA}-day moving average - 200 days to {data['date'][-1:][0]}')
    plt.xlabel("Date")
    plt.ylabel("Downloads")
    for field in ['osx-arm64', 'linux-aarch64', 'linux-64', 'osx-64', 'noarch']:
        plt.plot(data['date'][-MAX_PLOTS:], data[f'{field}_MA{MAA}'][-MAX_PLOTS:], label=f'{field}')

    x_labels = data['date'][-MAX_PLOTS::60]
    plt.xticks(data['date'][-MAX_PLOTS::60], x_labels)
    plt.legend(loc="upper left")
#    plt.show()
    plt.axhline()
    plt.grid()
    plt.savefig('../downloads.png')

    plt.figure(2)
    
    plt.suptitle(f"Percentage share of daily downloads")
    plt.title(f'{MAA}-day moving average - 200 days to {data['date'][-1:][0]}')
    plt.xlabel("Date")
    plt.ylabel("Percent of all downloads")
    for field in ['osx-arm64', 'linux-aarch64', 'linux-64', 'osx-64', 'noarch']:
        plt.plot(data['date'][-MAX_PLOTS:], data[f'{field}_MA{MAA}_percent'][-MAX_PLOTS:], label=f'{field}')

    x_labels = data['date'][-MAX_PLOTS::60]
    plt.xticks(data['date'][-MAX_PLOTS::60], x_labels)
    plt.legend(loc="upper left")
    plt.axhline()
    plt.grid()
    #    plt.show()
    plt.savefig('../percents.png')


arch_count = {}
for root, dir, files in os.walk(packages):
    for filename in files:
        with open(os.path.join(packages, filename), 'r') as f:
            line = f.readline()
            fields = line.rstrip().split('\t')
            data = {field : [] for field in fields}
            for line in f:
                if line.startswith("subdir"):
                    pass
                else:
                    arch = line.split("\t")[0]
                    count = line.split("\t")[1]
                    if not (arch in arch_count):
                        arch_count[arch] = {}
                    arch_count[arch] [filename.split(".")[0]] = int(count)

os.system("git checkout HEAD~7")
for root, dir, files in os.walk(packages):
    for filename in files:
        with open(os.path.join(packages, filename), 'r') as f:
            line = f.readline()
            fields = line.rstrip().split('\t')
            data = {field : [] for field in fields}
            for line in f:
                if line.startswith("subdir"):
                    pass
                else:
                    arch = line.split("\t")[0]
                    count = line.split("\t")[1]
                    filebase = filename.split(".")[0]
                    if not (arch in arch_count):
                        arch_count[arch] = {}
                    if filebase in arch_count[arch]:
                        arch_count[arch][filebase] -= int(count)


with open("../packages.md", "w") as f:

    print("# Top 10 packages by architecture", file = f)
    
    s = {}
    f.write('|')
    for arch in arch_count.keys():
        s[arch] = sorted(arch_count[arch].items(), key=lambda x: x[1], reverse = True)
        f.write(f'{arch} | ')
    print('', file = f)

    for i in range(0, 9):
        f.write('|')
        for arch in arch_count.keys():
            f.write(f'{s[arch][i]} |')
        print('', file = f)

    print("# First 10 missing packages in linux-aarch64 by linux-x86_64 rank", file = f)
    counter = 0 
    for i in s['linux-64']:
        if not (i[0] in arch_count['linux-aarch64']) and not(i[0] in arch_count['noarch']):
            print(i, file = f)
            counter += 1
        if counter >= 10:
            break
        
    print("# First 10 missing packages in osx-arm64 by osx-64 rank", file = f)
    counter = 0 
    for i in s['osx-64']:
        if not (i[0] in arch_count['osx-arm64']) and not(i[0] in arch_count['noarch']):
            print(i, file = f)
            counter += 1
        if counter >= 10:
            break
