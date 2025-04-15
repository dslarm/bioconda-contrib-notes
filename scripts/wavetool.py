#!/usr/bin/python
import argparse
import subprocess
import sys
import re
import os
import tempfile
import urllib.request as req
from pathlib import Path
import bs4 as bs
import json
from itertools import chain

def find_build_info(url):

    text = req.urlopen(url).read()
    tree = bs.BeautifulSoup(text, features='html.parser')


    conda_list_elt = tree.find('pre', attrs={'id' : 'condaFileData'})
    ents = conda_list_elt.get_text()
    packs = ents.split("dependencies:\n")[1].split("\n")
    packs = [p.split('- ')[1] for p in packs if p != '']
    return packs


url_re = re.compile('(https://wave.seqera.io/view/builds/.*_[0-9])')
def process(resdir, entry):
    missing = []
    with open(Path(resdir, entry)) as f:
        for line in f:
            if line.startswith("failed"):
                break
        for line in f:
            line = line.strip()
            m = url_re.search(line)
            if m:
                missing.append(find_build_info(m.group(1)))
    return missing

resdir = 'wave_results'
missing_dict = {}


orig_dir = os.getcwd()

with tempfile.TemporaryDirectory() as tmpdirname:
    temp_dir = Path(tmpdirname)
    os.chdir(temp_dir)

    subprocess.run(['git','clone', 'https://github.com/ewels/nf-core-arm-discovery'], stdout=open(os.devnull, 'wb'))
    os.chdir('nf-core-arm-discovery')
    
    for entry in os.listdir(resdir):
        if Path(resdir, entry).is_file():
            packs = process(resdir, entry)
            if not (entry in missing_dict):
                missing_dict [ entry ] = []
            missing_dict[entry] += packs

parser = argparse.ArgumentParser()
parser.add_argument('--output', type=str, default='wave_missing', help='base name of output files')

args = parser.parse_args()

output = args.output

os.chdir(orig_dir)

missing_pack = {}
for key in missing_dict:
    for packages in missing_dict[key]:
        for package in packages:
            if not ( package in missing_pack ):
                missing_pack[package] = []
            missing_pack[package].append(key)


        
d = { 'by_pipeline' : missing_dict,
      'by_package' : missing_pack
}

pipes_with_missing = [pipe for pipe in missing_dict.keys() if len(missing_dict[pipe] )> 0]
with open(output + '.json', 'w') as f:
    json.dump(d, f, indent = 4)

with open(output + '.txt', 'w') as f:

    print(f'Missing packages: {len(missing_pack.keys())}', file = f)
    print(f'Incomplete pipelines: {len(pipes_with_missing)} of {len(missing_dict.keys())}', file = f)

    print(f'Missing packages: {len(missing_pack.keys())}')
    print(f'Incomplete pipelines: {len(pipes_with_missing)} of {len(missing_dict.keys())}')

    print('\nPIPELINES SUMMARY:\n', file = f)
    summary = []
    
    for pipe in pipes_with_missing:
        summary.append( f'''{pipe} : {list(chain.from_iterable(missing_dict[pipe]))}''' )

    print('\n'.join(sorted(summary)), file = f)

    print('\nPACKAGES SUMMARY:\n', file = f)
    summary = []
    for pack in missing_pack:
        summary.append(f'''{pack} : {missing_pack[pack]}''')
    print('\n'.join(sorted(summary)), file = f)
    

