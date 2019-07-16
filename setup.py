from distutils.core import setup
from pip.req import parse_requirements
from distutils.command.install import install
import setuptools.command.build_py
import distutils.cmd
import distutils.log
import setuptools
import subprocess
import os
from subprocess import call


# Loading requirements
install_reqs = parse_requirements('requirements.txt', session=False)
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='seal_regression',
    version='0.0',
    author='Valentyn Melnychuk, Diana Devletshyna',
    author_email='v.melnychuk@campus.lmu.de, ',
    description='Implementation of Linear Regression on encrypted data with PySEAL',
    install_requires=reqs,
)
