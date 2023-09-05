#!/bin/python3

import os
import sys

prefixes = list()
suffixes = list()
for includer in sys.argv[1:]:
    if includer.startswith("*"): suffixes.append(includer[1:])
    else: prefixes.append(includer)

def has_valid_prefix (filepath: str):
    for prefix in prefixes:
        if filepath.startswith(prefix): return True
    if len(prefixes) <= 0: return True
    return False

def has_valid_suffix (filepath: str):
    for suffix in suffixes:
        if filepath.endswith(suffix): return True
    if len(suffixes) <= 0: return True
    return False

def is_valid_file(filepath: str):
    if not has_valid_prefix(filepath): return False
    if not has_valid_suffix(filepath): return False
    return True
                    

def get_src_files(root: str = ""):
    files = os.listdir(root if root != "" else None)
    i = 0
    while(i < len(files)):
        if os.path.isdir(os.path.join(root, files[i])):
            folder = files.pop(i)
            if folder == "__pycache__": continue
            if folder.startswith("."): continue
            for file in os.listdir(os.path.join(root, folder)): 
                if file == "__pycache__": continue
                files.append(os.path.join(folder, file))
        elif not is_valid_file(os.path.join(root, files[i])): files.pop(i)
        else: i += 1
    
    return files

for file in get_src_files(): print(file)
