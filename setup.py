"""
Torchserve Dashboard using streamlit
"""
from setuptools import find_packages, setup

dependencies = ["streamlit>=0.68", "click>=7.1.2"]

setup(
    name="torchserve_dashboard",
    version="0.1.0",
    url="https://github.com/cceyda/torchserve-dashboard",
    license="Apache Software License 2.0",
    author="Ceyda Cinarel",
    author_email="snu.ceyda@gmail.com",
    description="Torchserve dashboard using Streamlit",
    long_description=__doc__,
    packages=find_packages(exclude=["tests","assets"]),
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    install_requires=dependencies,
    entry_points="""
        [console_scripts]
        torchserve-dashboard=torchserve_dashboard.cli:main
        """,
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        "Development Status :: 4 - Beta",
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
