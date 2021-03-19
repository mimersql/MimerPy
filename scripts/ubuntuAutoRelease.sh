#!/bin/bash

# Checking if first commandline argument is set
if [ $# -eq 0 ]
  then
    echo "Error: missing first argument, TOKEN"
    exit 1
fi

# Checking if folder tmp exist
if [ -d "tmp" ]
then 
    echo "error, tmp folder already exsist"
    exit 1
fi

mkdir tmp 

cd tmp

git clone https://github.com/mimersql/MimerPy.git

cd MimerPy

# Getting latest tag number
latestTag=`git describe --tags $(git rev-list --tags --max-count=1)`

PTOKEN=$1

git checkout $latestTag

python3 -m pip install -U pip setuptools wheel

# Building a source distribution and one built distribution
python3 setup.py sdist bdist_wheel

python3 -m twine upload dist/* --username "__token__" --password $PTOKEN

cd ../..

rm -rf tmp

