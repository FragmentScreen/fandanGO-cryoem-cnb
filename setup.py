from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Load requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='fandanGO-cryoem-cnb',
    version='0.1.0',
    description='cryoem-cnb plugin of the FandanGO application',
    long_description=long_description,
    author='CNB-CSIC, Carolina Simon, Irene Sanchez',
    author_email='carolina.simon@cnb.csic.es, isanchez@cnb.csic.es',
    packages=find_packages(),
    install_requires=[requirements],
    entry_points={
        'fandango.plugin': 'fandanGO-cryoem-cnb = cryoemcnb'
    },
)
