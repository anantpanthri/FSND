#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**buildTocTree.py**

**Platform:**
	Windows, Linux, Mac Os X.

**Description:**
	Builds Sphinx documentation Toc Tree file.

**Others:**

"""

#**********************************************************************************************************************
#***	Future imports.
#**********************************************************************************************************************
from __future__ import unicode_literals

#**********************************************************************************************************************
#***	Encoding manipulations.
#**********************************************************************************************************************
import sys

def _setEncoding():
	"""
	Sets the Application encoding.
	"""

	reload(sys)
	sys.setdefaultencoding("utf-8")

_setEncoding()

#**********************************************************************************************************************
#***	External imports.
#**********************************************************************************************************************
import argparse
import glob
import os
import re

if sys.version_info[:2] <= (2, 6):
	from ordereddict import OrderedDict
else:
	from collections import OrderedDict

#**********************************************************************************************************************
#***	Internal imports.
#**********************************************************************************************************************
import foundations.decorators
import foundations.strings
import foundations.verbose
from foundations.io import File

#**********************************************************************************************************************
#***	Module attributes.
#**********************************************************************************************************************
__author__ = "Thomas Mansencal"
__copyright__ = "Copyright (C) 2008 - 2014 - Thomas Mansencal"
__license__ = "GPL V3.0 - http://www.gnu.org/licenses/"
__maintainer__ = "Thomas Mansencal"
__email__ = "thomas.mansencal@gmail.com"
__status__ = "Production"

__all__ = ["LOGGER",
		   "FILES_EXTENSION",
		   "TOCTREE_TEMPLATE_BEGIN",
		   "TOCTREE_TEMPLATE_END",
		   "buildTocTree",
		   "getCommandLineArguments",
		   "main"]

LOGGER = foundations.verbose.installLogger()

FILES_EXTENSION = ".rst"

TOCTREE_TEMPLATE_BEGIN = ["Welcome to {0} |version|'s documentation!\n",
						  "{0}\n",
						  "\n",
						  "Contents:\n",
						  "\n",
						  ".. toctree::\n",
						  " :maxdepth: 2\n",
						  " :numbered:\n"]
TOCTREE_TEMPLATE_END = ["Search:\n",
						"==================\n",
						"\n",
						"* :ref:`genindex`\n",
						"* :ref:`modindex`\n",
						"* :ref:`search`\n", ]

foundations.verbose.getLoggingConsoleHandler()
foundations.verbose.setVerbosityLevel(3)

#**********************************************************************************************************************
#***	Module classes and definitions.
#**********************************************************************************************************************
def buildTocTree(title, input, output, contentDirectory):
	"""
	Builds Sphinx documentation table of content tree file.

	:param title: Package title.
	:type title: unicode
	:param input: Input file to convert.
	:type input: unicode
	:param output: Output file.
	:type output: unicode
	:param contentDirectory: Directory containing the content to be included in the table of content.
	:type contentDirectory: unicode
	:return: Definition success.
	:rtype: bool
	"""

	LOGGER.info("{0} | Building Sphinx documentation index '{1}' file!".format(buildTocTree.__name__,
																			   output))
	file = File(input)
	file.cache()

	existingFiles = [foundations.strings.getSplitextBasename(item)
					 for item in glob.glob("{0}/*{1}".format(contentDirectory, FILES_EXTENSION))]
	relativeDirectory = contentDirectory.replace("{0}/".format(os.path.dirname(output)), "")

	tocTree = ["\n"]
	for line in file.content:
		search = re.search(r"`([a-zA-Z_ ]+)`_", line)
		if not search:
			continue

		item = search.groups()[0]
		code = "{0}{1}".format(item[0].lower(), item.replace(" ", "")[1:])
		if code in existingFiles:
			link = "{0}/{1}".format(relativeDirectory, code)
			data = "{0}{1}{2} <{3}>\n".format(" ", " " * line.index("-"), item, link)
			LOGGER.info("{0} | Adding '{1}' entry to Toc Tree!".format(buildTocTree.__name__,
																	   data.replace("\n", "")))
			tocTree.append(data)
	tocTree.append("\n")

	TOCTREE_TEMPLATE_BEGIN[0] = TOCTREE_TEMPLATE_BEGIN[0].format(title)
	TOCTREE_TEMPLATE_BEGIN[1] = TOCTREE_TEMPLATE_BEGIN[1].format("=" * len(TOCTREE_TEMPLATE_BEGIN[0]))
	content = TOCTREE_TEMPLATE_BEGIN
	content.extend(tocTree)
	content.extend(TOCTREE_TEMPLATE_END)

	file = File(output)
	file.content = content
	file.write()

	return True

def getCommandLineArguments():
	"""
	Retrieves command line arguments.

	:return: Namespace.
	:rtype: Namespace
	"""
	#
	parser = argparse.ArgumentParser(add_help=False)

	parser.add_argument("-h",
						"--help",
						action="help",
						help="'Displays this help message and exit.'")

	parser.add_argument("-t",
						"--title",
						type=unicode,
						dest="title",
						help="'Package title.'")

	parser.add_argument("-i",
						"--input",
						type=unicode,
						dest="input",
						help="'Input file to convert.'")

	parser.add_argument("-o",
						"--output",
						type=unicode,
						dest="output",
						help="'Output file.'")

	parser.add_argument("-c",
						"--contentDirectory",
						type=unicode,
						dest="contentDirectory",
						help="'Content directory.'")

	if len(sys.argv) == 1:
		parser.print_help()
		sys.exit(1)

	return parser.parse_args()

@foundations.decorators.systemExit
def main():
	"""
	Starts the Application.

	:return: Definition success.
	:rtype: bool
	"""

	args = getCommandLineArguments()
	return buildTocTree(args.title,
						args.input,
						args.output,
						args.contentDirectory)

if __name__ == "__main__":
	main()
