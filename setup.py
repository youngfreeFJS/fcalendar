#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for fcalendar package.
This file is for compatibility with traditional PyPI publishing workflows.
"""

from setuptools import setup, find_packages
import os

# Read version from __init__.py
def get_version():
    init_file = os.path.join(os.path.dirname(__file__), 'fcalendar', '__init__.py')
    with open(init_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '0.1.0'

# Read long description from README
def get_long_description():
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_file):
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

setup(
    name='fcalendar',
    version=get_version(),
    description='A Python calendar library with Chinese calendar support',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='youngfreefjs',
    url='https://github.com/youngfreefjs/fcalendar',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    install_requires=[
        'chinesecalendar>=1.9.0',
        'lunardate>=0.2.2',
    ],
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    keywords='calendar chinese lunar date',
    project_urls={
        'Source': 'https://github.com/youngfreefjs/fcalendar',
    },
)
