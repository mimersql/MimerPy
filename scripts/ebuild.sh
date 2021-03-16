#!/bin/bash

while getopts ":b, :c, :k" opt; do
  case $opt in
    c)
      sudo rm -rf build
      sudo rm -rf __pycache__
      sudo rm -rf dist
      sudo rm -rf mimerpy.egg-info
      sudo rm -rf mimerpy/__pycache__
      sudo python3 setup.py sdist
      sudo python3 -m twine upload dist/* --username "mimer" --password $MIMERPASS
      echo mimer
      ;;
    b)
      sudo rm -r build
      sudo rm -r __pycache__
      sudo rm -r dist
      sudo rm -r mimerpy.egg-info
      sudo rm -r mimerpy/__pycache__
      sudo pip3 uninstall mimerpy
      sudo python3 setup.py build
      ;;
    k)
    coverage run tests/testCursor.py TestCursorMethods
    coverage run --append tests/testConnection.py TestConnectionMethods
    coverage run --append tests/testScrollCursor.py TestScrollCursorMethods
    coverage run --append tests/testMonkey.py TestMonkey
    coverage html
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done
