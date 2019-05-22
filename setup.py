import setuptools
import sys

if sys.version_info.major == 2:
    python_version = 'python2-'
else:
    python_version = 'python'+str(sys.version_info.major)+str(sys.version_info.minor)+'-'

RPM_REQUIRED_DEPS = python_version+'requests'

## HACK FOR DEPS IN RPMS (taken from https://gist.github.com/primalmotion/1561092)
from setuptools.command.bdist_rpm import bdist_rpm
def custom_make_spec_file(self):
    spec = self._original_make_spec_file()
    lineDescription = "%description"
    spec.insert(spec.index(lineDescription) - 1, "requires: %s" % RPM_REQUIRED_DEPS)
    return spec
bdist_rpm._original_make_spec_file = bdist_rpm._make_spec_file
bdist_rpm._make_spec_file = custom_make_spec_file
## END OF HACK


with open("README.md", "r") as fh:

    long_description = fh.read()

setuptools.setup(

    name=python_version+'omsapi',

    version='0.5.0',

    author="Mantas Stankevicius",

    author_email="cmsoms-developers@cern.ch",

    description="python client for OMS API",

    long_description=long_description,

    long_description_content_type="text/markdown",

    url="https://gitlab.cern.ch/cmsoms/oms-api-client",

    packages=setuptools.find_packages(),

    install_requires=['requests'],

    classifiers=[

        "Programming Language :: Python :: 3",

        "License :: OSI Approved :: CERN License",

        "Operating System :: OS Independent",

    ],

)
