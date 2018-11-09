import setuptools

with open("README.md", "r") as fh:

    long_description = fh.read()

setuptools.setup(

     name='omsapi',  

     version='0.1',

     author="Mantas Stankevicius",

     author_email="cmsoms-developers@cern.ch",

     description="library for OMS API",

     long_description=long_description,

     long_description_content_type="text/markdown",

     url="https://gitlab.cern.ch/cmsoms/oms-api-client",

     packages=setuptools.find_packages(),

     install_requires=['requests'],

     classifiers=[

         "Programming Language :: Python :: 2",

         "License :: OSI Approved :: CERN License",

         "Operating System :: OS Independent",

     ],

 )