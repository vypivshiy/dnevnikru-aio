from setuptools import setup
from pathlib import Path

from dnevnikru_aio import __version__ as v

this_directory = Path(__file__).parent
long_description = (this_directory / "Readme.md").read_text()

setup(
    name='dnevnikru_aio',
    version=v,
    packages=['dnevnikru_aio'],
    url='https://github.com/vypivshiy/dnevnikru-aio',
    license='GPL3',
    author='vypivshiy',
    author_email='',
    description='dnevnik.ru unofficial API asyncio parser',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'aiohttp',
        'bs4',
        'lxml'
    ],
)
