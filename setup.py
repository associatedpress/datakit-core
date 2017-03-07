"""

Datakit
-------

`datakit-core` is a pluggable command-line tool for creating custom
data science workflows.

It's intended to be used with one or more compatible plugins. Check out the
 `Associated Pess Github account <https://github.com/search?q=topic%3Adatakit-cli+org%3Aassociatedpress&type=Repositories>`_
 for an evolving set of plugins or learn
 `how to write your own <http://datakit-core.readthedocs.io/en/latest/developers.html#creating-plugins>`_.

"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='datakit-core',
    version='0.2.1',
    description="A pluggable command-line tool for custom data science workflows.",
    long_description=__doc__,
    author="Serdar Tumgoren",
    author_email='zstumgoren@gmail.com',
    url='https://github.com/associatedpress/datakit-core',
    license="ISCL",
    keywords='datakit',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Environment :: Console',
    ],
    packages=['datakit'],
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
    tests_require=['pytest', 'pytest-catchlog', 'tox'],
    zip_safe=False,
)
