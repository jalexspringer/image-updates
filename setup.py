#!/usr/bin/env python

from setuptools import setup

setup(
    name="image-updates",
    version='0.1.2',
    py_modules=['cli','utils'],
    install_requires=[
        'Click',
        'matplotlib',
        'requests'
    ],
    entry_points='''
        [console_scripts]
        image-updates=cli:create_plot_file
    ''',
)
