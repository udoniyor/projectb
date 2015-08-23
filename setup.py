"""
Setup script for ProjectB.
"""

from setuptools import setup, find_packages

setup(name='projectb',
      version='0.0.1',
      author='Doniyor Ulmasov',
      author_email='du514@ic.ac.uk',
      description='A Python package for GUI Bayesian optimization',
      url='http://github.com/udoniyor/projectb',
      license='Simplified BSD',
      packages=find_packages(),
      package_data={'': ['*.txt', '*.npz']},
      install_requires=['numpy', 'scipy', 'matplotlib', 'mwhutils', 'pygp', 'pybo'])