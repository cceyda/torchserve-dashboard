"""
Torchserve Dashboard using streamlit
"""
from setuptools import find_packages, setup


dependencies = ["streamlit==0.82.0", "click<8.0,>=7.0", "httpx>=0.16.0"]

setup(
    name="torchserve_dashboard",
    version="v0.4.0",
    url="https://github.com/cceyda/torchserve-dashboard",
    license="Apache Software License 2.0",
    author="Ceyda Cinarel",
    author_email="15624271+cceyda@users.noreply.github.com",
    description="Torchserve dashboard using Streamlit",
    long_description=__doc__,
    packages=find_packages(exclude=["tests", "assets"]),
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
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
    ],
)
