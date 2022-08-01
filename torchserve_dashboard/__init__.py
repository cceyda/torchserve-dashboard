"""Root package info."""
import logging as __logging
import os
from  datetime import date

__version__ = 'v0.6.0'

__author_name__ = 'Ceyda Cinarel'
__author_email__ = '15624271+cceyda@users.noreply.github.com'
__license__ = 'Apache Software License'
__copyright__ = f'Copyright (c) 2020-{date.today().year}, {__author_name__}.'
__homepage__ = 'https://github.com/cceyda'
__download_url__ = 'https://github.com/cceyda/torchserve-dashboard'
# this has to be simple string, see: https://github.com/pypa/twine/issues/522
__docs__ = "PACKAGE_DESCRIPTION"
__long_docs__ = """
What is it?
-----------
Describe the package

Second title
----------------
Description

Another title
------------------
Description
"""

_logger = __logging.getLogger("torchserve_dashboard")
_logger.addHandler(__logging.StreamHandler())
_logger.setLevel(__logging.INFO)

_PACKAGE_ROOT = os.path.dirname(__file__)
_PROJECT_ROOT = os.path.dirname(_PACKAGE_ROOT)
