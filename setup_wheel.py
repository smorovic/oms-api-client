import setuptools
import sys
import subprocess

if sys.version_info.major == 2:
    print("Python 2 is not supported")
    sys.exit(2)
else:
    python_version = 'python'+str(sys.version_info.major)+str(sys.version_info.minor)+'-'

RPM_REQUIRED_DEPS = python_version+'requests'

#additional package required if using kerberos auth to access OIDC protected resources
#RPM_REQUIRED_DEPS = python_version+'requests'+',auth-get-sso-cookie'

## HACK FOR DEPS IN RPMS (taken from https://gist.github.com/primalmotion/1561092)

#fetch version from the latest tag
proc = subprocess.Popen("git describe --tags | sed 's/^v//' | awk '{split($0,a,\"-\"); print a[1]}'",
                        shell=True,
                        stdout=subprocess.PIPE)
ver=proc.communicate()[0].decode()

#with open("README.md", "r") as fh:

    #long_description = fh.read()

setuptools.setup(

    name='omsapi',

    version=ver,

    author="Mantas Stankevicius",

    author_email="cmsoms-developers@cern.ch",

    description="python client for OMS API",

    #long_description=long_description,

    long_description_content_type="text/markdown",

    url="https://gitlab.cern.ch/cmsoms/oms-api-client",

    packages=setuptools.find_packages(),

    include_package_data=True,

    classifiers=[

        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: CERN License",
        "Operating System :: OS Independent",

    ],
    install_requires = ['requests']

)
