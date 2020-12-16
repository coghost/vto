#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from vto import VERSION

setup(
    name='vto',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['*.tpl', '*.md']},
    author='lihe',
    author_email='imanux@sina.com',
    url='https://github.com/coghost/vto',
    description='vto',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    license='GPL',
    install_requires=['requests', 'clint', 'click'],
    project_urls={
        'Bug Reports': 'https://github.com/coghost/vto/issues',
        'Source': 'https://github.com/coghost/vto',
    },
    python_requires='>=3.8',
    classifiers=[
        'Programming Language :: Python :: 3.8',
    ],
    keywords=['wow', 'colorful', 'vivid', 'awesome', 'terminal'],
)
