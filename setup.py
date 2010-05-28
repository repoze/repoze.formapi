##############################################################################
#
# Copyright (c) 2008 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

import os
from setuptools import setup, find_packages, Extension

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='repoze.formapi',
      version = '0.5.0',
      description='Minimalistic form library.',
      long_description=read('README.txt') + read('src/repoze/formapi/README.txt'),
      keywords = "forms html validation marshalling",
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP'],
      author="Malthe Borch",
      author_email="repoze-dev@lists.repoze.org",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['repoze', ],
      install_requires=[
          'setuptools',
          ],
      include_package_data = True,
      zip_safe = False,
      test_suite="repoze.formapi.tests.test_suite",
      )
