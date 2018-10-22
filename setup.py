#!/usr/bin/env python
# coding: utf-8

from os import path
from pathlib import Path

try:
    from pip._internal.req import parse_requirements
except ImportError:
    from pip.req import parse_requirements

from setuptools import setup, find_packages


def read_file(filename):
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here, filename), encoding='utf-8') as f:
        return f.read()


def requirements(filename):
    """Parse requirements from requirements.txt."""
    path = str(Path(filename))
    reqs = parse_requirements(path, session=False)
    return [str(req.req) for req in reqs]


setup(
    name='music-dl',
    version='0.1.3',
    description='Command line tool to download music from YouTube and SoundCloud',
    long_description=read_file('README.md'),
    url='https://github.com/gumob/music-dl',
    author='Gumob',
    license='MIT',
    keywords=['youtube', 'soundcloud', 'download', 'mp3', 'm4a', 'flac'],
    author_email='hello@gumob.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3.4',
    platforms=['posix'],
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=requirements('requirements.txt'),
    entry_points={
        'console_scripts': [
            'music-dl=music_dl:__init__.main',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/gumob/music-dl/issues',
        'Funding': 'https://donate.pypi.org',
        'Source': 'https://github.com/gumob/music-dl/',
    },
    test_suite='tests',
)
