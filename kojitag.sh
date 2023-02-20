#!/bin/bash -x
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

echo "BUILDING RPMS..."
/usr/bin/python3.8 setup.py bdist_rpm --python /usr/bin/python3.8 --build-requires python38,python38-setuptools --release 0.el8

#srcrpm=`ls rpmbuild/SRPMS/oms-portal-gui-*.src.rpm`
pkg="python38-omsapi"
srcrpm=`ls -t dist/${pkg}-*.src.rpm | head -1`
rpmname=`/usr/bin/python3 -c "import os,sys; p = sys.argv[1].split('/')[-1]; print(p[:p.find('.src.rpm')])" $srcrpm`

echo "RUNNING WITH KOJI USER ${KOJICI_USER}"
echo ${KOJICI_PWD} | kinit ${KOJICI_USER}@CERN.CH


if [ -z $1 ]; then
  echo "Koji pre-add package to testing: $srcrpm"
  koji add-pkg --owner=${KOJICI_USER} cmsoms8s-testing ${pkg}
  echo "Koji build source rpm: $srcrpm"
  koji build --wait cmsoms8s $srcrpm
  #echo "Koji pre-add package to qa: $srcrpm"
  #koji add-pkg --owner=${KOJICI_USER} cmsoms8s-qa ${pkg}
  #koji tag cmsoms8s-qa $rpmname
  echo "Koji pre-add package to production: $srcrpm"
  koji add-pkg --owner=${KOJICI_USER} cmsoms8s-stable ${pkg}
  koji tag cmsoms8s-stable $rpmname
else
  echo "Koji SCRATCH build"
  #koji build --scratch --wait cmsoms8s $srcrpm
fi
