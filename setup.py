"""
https://habr.com/ru/company/skillfactory/blog/506352/
"""
from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["xmljson"]

setup(
    name="objtreexml",
    version="0.0.1",
    author="a.v.e.r",
    author_email="a.v.e.r@mail.ru",
    description="A package to convert object trees to xml and back",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/aver007/obj-tree-to-xml",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
