#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

setup(
    name='datakit-core',
    version='0.1',
    description="Tool for managing data project life cycle.",
    long_description=readme,
    author="Serdar Tumgoren",
    author_email='zstumgoren@gmail.com',
    url='https://github.com/zstumgoren/datakit-core',
    license="ISCL",
    keywords='datakit-core',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Environment :: Console',
    ],
    packages=[
        'datakit',
        'datakit.cli',
    ],
    package_dir={'datakit': 'datakit'},
    include_package_data=True,
    install_requires=['cliff'],
    entry_points={
        'console_scripts': [
            'datakit=datakit.main:main',
        ],
        'datakit.plugins': []
    },
    test_suite='tests',
    tests_require=['pytest', 'tox'],
    zip_safe=False,
)
