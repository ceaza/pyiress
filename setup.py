from distutils.core import setup
import sys

install_requires_list = ['zeep', 'pandas',]

# Long description to be published in PyPi
LONG_DESCRIPTION = """
**PyIress** is a Python interface to the **Iress Pro Desktop Web Services
(IPD)** SOAP client (non free), with some convenience functions for retrieving
Iress data specifically. This package requires valid credentials for this
API.

For the documentation please refer to README.md inside the package or on the
GitHub (https://github.com/ceaza/pyiress/blob/master/README.md).
"""

_URL = 'https://github.com/ceaza/pyiress'
_VERSION = '0.0.1'


setup(name='PyIress',
      version=_VERSION,
      description='Python interface to the Iress Pro Desktop Web Services API',
      long_description=LONG_DESCRIPTION,
      url=_URL,
      download_url=_URL + '/archive/' + _VERSION + '.zip',
      install_requires = install_requires_list,
      author='Charles Allderman',
      author_email='charles@allderman.com',
      license='MIT License',
      packages=['pyiress'],
      classifiers=['Programming Language :: Python :: 3', ]
      )
