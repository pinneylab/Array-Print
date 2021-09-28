from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
	name = 'array-print',
	version = '0.1.0',
	url = 'https://github.com/mypackage.git',
	author = 'Micah Olivas',
	author_email = '',
	description = 'Scienion Print Array Generation',
	packages = find_packages(),    
	install_requires = requirements,
)
