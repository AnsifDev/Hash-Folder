#!/bin/python3

import os
import sys


resources = """<?xml version="1.0" encoding="UTF-8"?>\n<gresources>\n\t<gresource prefix="/%application-id%">\n"""

def get_src_files(root: str = None):
    files = os.listdir(root)
    i = 0
    while(i < len(files)):
        if os.path.isdir(os.path.join(root if root else "", files[i])):
            folder = files.pop(i)
            if folder == "__pycache__": continue
            if os.path.join(root if root else "", folder) == "src/resources/icons": continue
            if os.path.join(root if root else "", folder) == "src/resources/app": continue
            for file in os.listdir(os.path.join(root if root else "", folder)): 
                if file == "__pycache__": continue
                files.append(os.path.join(folder, file))
        else: i += 1
    return files

files = get_src_files("src/resources")
resources = resources.replace("%application-id%", sys.argv[1].replace(".", "/"))
for file in files: resources += """\t\t<file>%file%</file>\n""".replace("%file%", file)
resources += """\t</gresource>\n</gresources>\n"""

with open("resources.xml", "w") as file: file.write(resources)