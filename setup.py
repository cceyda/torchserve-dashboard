"""
Torchserve Dashboard using streamlit
"""
import os

from setuptools import find_packages, setup

import torchserve_dashboard
from torchserve_dashboard import setup_tools

PATH_ROOT = os.path.dirname(__file__)


# https://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-extras
# Define package extras. These are only installed if you specify them.
# From remote, use like `pip install deemea_torch[dev, docs]`
# From local copy of repo, use like `pip install ".[dev, docs]"`
def _prepare_extras():
    extras = {
        'docs': setup_tools.load_requirements(file_name='docs.txt'),
        'extra': setup_tools.load_requirements(file_name='extra.txt'),
        'test': setup_tools.load_requirements(file_name='test.txt'),
    }
    # print(extras)
    extras['dev'] = extras['extra'] + extras['test'] + extras['docs']
    extras['all'] = extras['dev']
    return extras


# Configure the package build and distribution
#   @see https://github.com/pypa/setuptools_scm
#
# To record the files created use:
#   python setup.py install --record files.txt
setup(
    name='torchserve_dashboard',  # Required
    version=torchserve_dashboard.__version__,  # Required
    url=torchserve_dashboard.__homepage__,  # Optional
    license=torchserve_dashboard.__license__,  # Optional
    author=torchserve_dashboard.__author_name__,  # Optional
    author_email=torchserve_dashboard.__author_email__,  # Optional
    download_url=torchserve_dashboard.__download_url__,  # Optional
    description='Torchserve dashboard using Streamlit',
    long_description=setup_tools.read_file(os.path.join(
        PATH_ROOT, 'README.md')),  # Optional
    long_description_content_type='text/markdown',  # Optional

    # This field adds keywords for your project which will appear on the
    # project page. What does your project relate to?
    # A list of strings or a comma-separated string providing descriptive
    # meta-data.
    keywords=[
        'machine learning', 'torchserve', 'dashboard', 'torchserve management',
        'model inference'
    ],  # Optional

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    packages=find_packages(exclude=['tests', 'assets']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    setup_requires=[],
    install_requires=setup_tools.load_requirements(
        file_name='install.txt'),  # Optional
    extras_require=_prepare_extras(),
    python_requires='>=3.7',

    # test_suite='setup.get_test_suite',
    # tests_require=["coverage"],
    project_urls={
        "Bug Tracker": torchserve_dashboard.__download_url__ + "/issues",
        # "Documentation": "https://deemea_torch.rtfd.io/en/latest/",
        "Source Code": torchserve_dashboard.__download_url__,
    },

    # Classifiers help users find your project by categorizing it.
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[
        'Natural Language :: English',
        # How mature is this project? Common values are
        #   3 - Alpha, 4 - Beta, 5 - Production/Stable
        'Development Status :: 4 - Beta',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'License :: OSI Approved :: {}'.format(
            torchserve_dashboard.__license__),
        'Operating System :: OS Independent',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
    ],
    entry_points="""
        [console_scripts]
        torchserve-dashboard=torchserve_dashboard.cli:main
        """,
)
