#!env python3
import subprocess
import sys
import re
import os
subprocess.run(['git','checkout', 'master'])

platforms = re.compile('- linux-aarch64')
platforms_osx = re.compile('- osx-arm64')
extra = re.compile('extra:')
set_name_pattern = re.compile(r'\{% set name = ')
set_version_pattern = re.compile(r'\{% set version = "(.*)"')
name_pattern = re.compile('name: (.+)')
pin_pattern = re.compile('pin_subpackage')
version_pattern = re.compile('version: (.+)')
build_number_pattern = re.compile(r'number: (\d+)')
generic = re.compile("noarch: generic")
for i in sys.argv[1:]:
         try:
                  with open(f'recipes/{i}/meta.yaml', 'r') as f:
                           cont = f.read()
                           if generic.search(cont):
                                    print (f'{i} is generic')
                                    continue
                           if platforms.search(cont):
                                    print (f'{i} has aarch64 support')
                                    continue
                           
                           if not set_name_pattern.search(cont):
                                    name = name_pattern.search(cont).group(1)
                                    print(f"adding name: {name}")
                                    cont = f'{{% set name = "{name}" %}}\n' + cont

                                    cont = re.sub(name_pattern, f'name: {{{{name}}}}', cont, 1)

                           m = set_version_pattern.search(cont)
                           if m:
                                    version = m.group(1)
                           else:
                                    m = version_pattern.search(cont)
                                    version = m.group(1)
                           if not pin_pattern.search(cont):
                                    c = build_number_pattern.search(cont)
                                    print(c.group(0))
                                    if (version.startswith("0")):
                                             pinline = '\n  run_exports:\n    - {{ pin_subpackage(name, max_pin = "x.x") }}\n'
                                    else:
                                             pinline = '\n  run_exports:\n    - {{ pin_subpackage(name, max_pin = "x") }}\n'
                                    cont = re.sub(build_number_pattern, c.group(0) + pinline, cont)
                                             
                           archline = "extra:\n  additional-platforms:\n    - linux-aarch64\n"

                           if 'OSX_TOO' in os.environ:
                                    archline += "    - osx-arm64\n"
                                    plats = 'osx-arm64, linux-aarch64'
                           else:
                                    plats = 'linux-aarch64'
                           
                           if not extra.search(cont):
                                    cont += archline
                           else:
                                    cont = re.sub(extra, archline, cont)


                           m = build_number_pattern.search(cont)
                           num = m.group(1)
                           num = int(num) + 1
                           cont = re.sub(build_number_pattern, f'number: {num}', cont)

                           f.close()
                           print(f'making new recipe {i}')                           
                           subprocess.run(['git','checkout','-b', f'{i}-aarch64'])
                           subprocess.run(['git','checkout', f'{i}-aarch64'])
                           print(f'subprocess ..')                           
                           with open(f'recipes/{i}/meta.yaml', 'w') as f:
                                    f.write(cont)

                           subprocess.run(['git', 'commit', '-a', '-m', f'{i}: add {plats}'])
                           subprocess.run(['git','push'])
                           subprocess.run(['git', 'checkout', 'master'])
                           print(f'made new recipe {i}')
         except FileNotFoundError:
                  print(f'no recipe {i}')
