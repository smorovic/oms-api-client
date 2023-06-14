#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
PYVER=`/usr/bin/python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'`

rm -rf venv

if [ $PYVER == "3.8" ]; then
  #RHEL8 and python3.8
  python3.8 -m venv venv
else
  virtualenv-3 venv
fi
source venv/bin/activate
pip3 install --upgrade pip
pip3 install --upgrade setuptools
pip3 install --upgrade twine
pip3 install --upgrade wheel

rm -rf dist/*.whl
python3 setup_wheel.py bdist_wheel
wheelfile=`ls dist/*.whl -t | head -n 1`
echo "wheel file: ${wheelfile}"
python3 -m twine upload --verbose --repository gitlab ${wheelfile}

rm -rf venv
