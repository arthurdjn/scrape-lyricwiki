# -*- coding: utf-8 -*-
# Created on Wed Jan 29 00:11:30 2020
# @author: arthurd


from setuptools import setup, find_packages


def readme_data():
    with open("README.md", "r") as fh:
        long_description = fh.read()
    return long_description


find_packages()

setup(name='lyricsfandom',
      version='0.2',
      description='Scrape songs on LyricWiki.',
      long_description=readme_data(),
      long_description_content_type="text/markdown",
      url='https://github.com/arthurdjn/scrape-lyricwiki',
      author='Arthur Dujardin',
      author_email='arthur.dujardin@ensg.eu',
      license='MIT Licence',

      install_requires=['urllib3', 'beautifulsoup4', 'unidecode'],
      packages=find_packages(),
      zip_safe=False,
      classifiers=[
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 5 - Production/Stable',
          # Indicate who your project is intended for
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],

      )
