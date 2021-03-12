#!/bin/bash

PTOKEN=

if exist tmp (
    echo "error, tmp folder already exsist"
    pause
    exit 1
)

mkdir tmp 

cd tmp

git clone https://github.com/mimersql/MimerPy.git

cd MimerPy

latestTag=git describe --tags $(git rev-list --tags --max-count=1)

git checkout $latestTag

python3 -m pip install -U pip setuptools wheel

# Building a source distribution and one built distribution
python3 setup.py sdist bdist_wheel

python3 -m twine upload dist/* --username "__token__" --password $PTOKEN

cd ../..

rm -rf tmp

