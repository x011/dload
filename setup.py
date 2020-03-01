'''
 Project: iptv
 Time: 22/02/2020 02:53
 '''
import setuptools


with open("README.md", "r") as fh:

	long_description = fh.read()

setuptools.setup(
	python_requires='>=3.6',

	install_requires = ['requests>=2.11.1'],

	name='dload',

	version='0.6',

	#scripts=['pyupdown', "__init__.py"],

	author="xTudo",

	author_email="dload@11.to",

	description="A multipurpose downloader for python >= 3.6",

	long_description=long_description,

	long_description_content_type="text/markdown",

	url="https://github.com/x011/dload",

	packages=setuptools.find_packages(),


	classifiers=[

		"Programming Language :: Python :: 3.6",

		"License :: OSI Approved :: MIT License",

		"Operating System :: OS Independent",

	],

)