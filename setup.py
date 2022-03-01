from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in ganapathy_pavers/__init__.py
from ganapathy_pavers import __version__ as version

setup(
	name="ganapathy_pavers",
	version=version,
	description="Ganapathy Pavers",
	author="Thirvusoft",
	author_email="careers@thirvusoft.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
