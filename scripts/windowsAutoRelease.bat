:: @echo off
:: Arg 1 is the private token for PyPI or TestPyPI 

:: Checking if first commandline argument is set
if [%1]==[] (
    echo "Error: missing first argument, TOKEN"
    pause
    exit 1
)

:: Checking if folder tmp exist
if exist tmp (
    echo "Error: tmp folder already exsist"
    pause
    exit 1
)

powershell mkdir tmp 

cd tmp

powershell git clone https://github.com/mimersql/MimerPy.git

cd MimerPy

:: Getting latest tag 
for /f %%a in (' powershell git rev-list --tags --max-count=1 ') do (set "Tag=%%a")

:: Getting latest tag number
for /f %%a in (' powershell git describe --tags %Tag% ') do (set "latestTag=%%a")

powershell git checkout %latestTag%

powershell py -m pip install -U pip setuptools wheel

:: Building a source distribution and one built distribution
powershell py setup.py sdist bdist_wheel

:: Gettings first argument
set ptoken=%1

powershell py -m twine upload dist/* --username "__token__" --password %ptoken%

cd ../..

powershell rm -Force -Recurse tmp

pause
