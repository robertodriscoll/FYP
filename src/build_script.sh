#!/usr/bin/env bash

#build executable for three network
pyinstaller webtext_main.py --onefile -n three --clean --distpath ../

#build executable for eir network
sed s/three/eir/ < webtext_main.py > webtext_main_temp.py 
pyinstaller webtext_main_temp.py --onefile -n eir --clean --distpath ../

rm webtext_main_temp.py
rm -rf __pycache__
rm -rf build
rm *.spec