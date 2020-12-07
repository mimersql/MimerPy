#!/bin/bash

sp='/-\|'
printf ' '
lap=1

printstuff() {
  if [ `echo "$lap % 100" | bc` -eq 0 ]
  then
  printf '\b%.1s ' "#"
  fi
  lap=$((lap + 1))

  if [ `echo "$lap % 1000" | bc` -eq 0 ]
  then
  exit
  fi
}

spin() {
  printf '\b%.1s' "$sp"
   sp=${sp#?}${sp%???}
}
endspin() {
  printf "\r%s\n" "$@"
}

while getopts ":b, :c, :C, :s, :S, :p, :P, :z, :m, :M, :j, :J, :k, :d" opt; do
  case $opt in
    b)
      sudo rm -r build
      sudo rm -r __pycache__
      sudo rm -r dist
      sudo rm -r mimerpy.egg-info
      sudo rm -r mimerpy/__pycache__
      sudo pip3 uninstall mimerpy
      sudo python3 setup.py build
      sudo python3 setup.py install
      echo ""
      echo ""
      ;;
    k)
    coverage run tests/testCursor.py TestCursorMethods
    coverage run --append tests/testConnection.py TestConnectionMethods
    coverage run --append tests/testScrollCursor.py TestScrollCursorMethods
    coverage run --append tests/testMonkey.py TestMonkey
    coverage html
      ;;
    c)
      python3 tests/testCursor.py TestCursorMethods
      ;;
    C)
      python3 tests/testConnection.py TestConnectionMethods
      ;;
    P)
      python3 tests/testScrollCursor.py TestScrollCursorMethods
      ;;
    s)
      python3 tests/testCursor.py TestCursorMethods.test_insert_nclob
      ;;
    S)
      python3 tests/testConnection.py TestConnectionMethods.test_with_commit_insert
      ;;
    p)
      python3 tests/testScrollCursor.py TestScrollCursorMethods.test_next_noselect
      ;;
    m)
      python3 tests/testMonkey.py TestMonkey.test_condis
      ;;
    M)
      python3 tests/testMonkey.py TestMonkey
      ;;
    z)
      python3 tests/dropdb.py
      ;;
    d)
      mimcontrol testpy2 -k
      mimcontrol testpy2 -s
      ;;
    j)
      while printstuff
      do
        printf '\b%.1s' "$sp"
        sp=${sp#?}${sp%???}
      done
      endspin
      ;;
    J)
      echo -n '#####                     (33%)\r'
      sleep 1
      echo -n '#############             (66%)\r'
      sleep 1
      echo -n '#######################   (100%)\r'
      sleep 1
      echo -n '\n'

      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done
