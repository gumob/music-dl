#!/usr/bin/env python
# coding: utf-8
import re
from os import path
from pathlib import Path

try:
    from pip._internal.req import parse_requirements
except ImportError:
    from pip.req import parse_requirements

from setuptools import setup, find_packages

root_dir = path.abspath(path.dirname(__file__))

package_name = 'music_dl'


def read_file(filename):
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here, filename), encoding='utf-8') as f:
        return f.read()


def requirements(filename):
    """Parse requirements from requirements.txt."""
    req_file = str(Path(filename))
    req_list = parse_requirements(req_file, session=False)
    return [str(req.req) for req in req_list]


with open(path.join(root_dir, package_name, '__init__.py')) as f:
    init_text = f.read()
    version = re.search(r'__version__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    license = re.search(r'__license__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    author = re.search(r'__author__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    author_email = re.search(r'__author_email__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    url = re.search(r'__url__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    copyright = re.search(r'__copyright__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)

assert version
assert license
assert author
assert author_email
assert url

setup(
    name=package_name,
    version=version,
    description='Command line tool to download music from YouTube and SoundCloud',
    long_description=read_file('README.md'),
    url=url,
    author=author,
    license=license,
    keywords=['youtube', 'soundcloud', 'download', 'mp3', 'm4a', 'flac', 'youtube-dl', 'youtubedl'],
    author_email=author_email,
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
            'music-dl=music_dl:main',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/gumob/music-dl/issues',
        'Funding': 'https://donate.pypi.org',
        'Source': 'https://github.com/gumob/music-dl/',
    },
    test_suite='tests',
)
