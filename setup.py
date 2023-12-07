#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 11:45:01 2023

@author: karinmorandell
"""

from setuptools import setup, find_packages

setup(
    name='sheets2CV',  # Replace with your package's name
    version='231206',  # The initial release version
    author='Karin Morandell',  # Your name or your organization’s name
    author_email='karinmorandell.pro@gmail.com',  # Your email
    description='Generate CV from Google sheets',  # Short description
    long_description=open('README.md').read(),  # Long description read from the readme file
    long_description_content_type='text/markdown',  # Long description content type
    packages=find_packages(exclude=['tests*']),  # List of all python modules to be installed
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],    
    python_requires='>=3.7',  # Minimum version requirement of the package
    install_requires=[
        'pandas',  # For data manipulation and analysis
         'numpy',  # for numerical operations
         'importlib',
         'reportlab',  # For PDF generation and handling
         'Pillow>=8.0',  # Python Imaging Library (PIL) Fork for image processing
         ]
)
