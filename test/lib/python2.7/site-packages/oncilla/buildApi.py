#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**buildApi.py**

**Platform:**
	Windows, Linux, Mac Os X.

**Description:**
	Builds Sphinx documentation Api files.

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
import os
import shutil

if sys.version_info[:2] <= (2, 6):
	from ordereddict import OrderedDict
else:
	from collections import OrderedDict

#**********************************************************************************************************************
#***	Internal imports.
#**********************************************************************************************************************
import foundations.common
import foundations.decorators
import foundations.exceptions
import foundations.strings
import foundations.verbose
import foundations.walkers
from foundations.io import File

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "libraries"))
import python.pyclbr as moduleBrowser

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
		   "SANITIZER",
		   "importSanitizer",
		   "buildApi",
		   "getCommandLineArguments",
		   "main"]

LOGGER = foundations.verbose.installLogger()

FILES_EXTENSION = ".rst"

TOCTREE_TEMPLATE_BEGIN = ["Api\n",
						  "====\n",
						  "\n",
						  "Modules Summary:\n",
						  "\n",
						  ".. toctree::\n",
						  "   :maxdepth: 1\n",
						  "\n"]

TOCTREE_TEMPLATE_END = []

SANITIZER = os.path.join(os.path.dirname(__file__), "defaultSanitizer.py")

foundations.verbose.getLoggingConsoleHandler()
foundations.verbose.setVerbosityLevel(3)

#**********************************************************************************************************************
#***	Module classes and definitions.
#**********************************************************************************************************************
def importSanitizer(sanitizer):
	"""
	Imports the sanitizer python module.

	:param sanitizer: Sanitizer python module file.
	:type sanitizer: unicode
	:return: Module.
	:rtype: object
	"""

	directory = os.path.dirname(sanitizer)
	not directory in sys.path and sys.path.append(directory)

	namespace = __import__(foundations.strings.getSplitextBasename(sanitizer))
	if hasattr(namespace, "bleach"):
		return namespace
	else:
		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' is not a valid sanitizer module file!".format(sanitizer))

def buildApi(packages, input, output, sanitizer, excludedModules=None):
	"""
	Builds the Sphinx documentation API.

	:param packages: Packages to include in the API.
	:type packages: list
	:param input: Input modules directory.
	:type input: unicode
	:param output: Output reStructuredText files directory.
	:type output: unicode
	:param sanitizer: Sanitizer python module.
	:type sanitizer: unicode
	:param excludedModules: Excluded modules.
	:type excludedModules: list
	:return: Definition success.
	:rtype: bool
	"""

	LOGGER.info("{0} | Building Sphinx documentation API!".format(buildApi.__name__))

	sanitizer = importSanitizer(sanitizer)

	if os.path.exists(input):
		shutil.rmtree(input)
		os.makedirs(input)

	excludedModules = [] if excludedModules is None else excludedModules

	packagesModules = {"apiModules": [],
					   "testsModules": []}
	for package in packages:
		package = __import__(package)
		path = foundations.common.getFirstItem(package.__path__)
		packageDirectory = os.path.dirname(path)

		for file in sorted(
				list(foundations.walkers.filesWalker(packageDirectory, filtersIn=("{0}.*\.ui$".format(path),)))):
			LOGGER.info("{0} | Ui file: '{1}'".format(buildApi.__name__, file))
			targetDirectory = os.path.dirname(file).replace(packageDirectory, "")
			directory = "{0}{1}".format(input, targetDirectory)
			if not foundations.common.pathExists(directory):
				os.makedirs(directory)
			source = os.path.join(directory, os.path.basename(file))
			shutil.copyfile(file, source)

		modules = []
		for file in sorted(
				list(foundations.walkers.filesWalker(packageDirectory, filtersIn=("{0}.*\.py$".format(path),),
													 filtersOut=excludedModules))):
			LOGGER.info("{0} | Python file: '{1}'".format(buildApi.__name__, file))
			module = "{0}.{1}".format((".".join(os.path.dirname(file).replace(packageDirectory, "").split("/"))),
									  foundations.strings.getSplitextBasename(file)).strip(".")
			LOGGER.info("{0} | Module name: '{1}'".format(buildApi.__name__, module))
			directory = os.path.dirname(os.path.join(input, module.replace(".", "/")))
			if not foundations.common.pathExists(directory):
				os.makedirs(directory)
			source = os.path.join(directory, os.path.basename(file))
			shutil.copyfile(file, source)

			sanitizer.bleach(source)

			if "__init__.py" in file:
				continue

			rstFilePath = "{0}{1}".format(module, FILES_EXTENSION)
			LOGGER.info("{0} | Building API file: '{1}'".format(buildApi.__name__, rstFilePath))
			rstFile = File(os.path.join(output, rstFilePath))
			header = ["_`{0}`\n".format(module),
					  "==={0}\n".format("=" * len(module)),
					  "\n",
					  ".. automodule:: {0}\n".format(module),
					  "\n"]
			rstFile.content.extend(header)

			functions = OrderedDict()
			classes = OrderedDict()
			moduleAttributes = OrderedDict()
			for member, object in moduleBrowser._readmodule(module, [source, ]).iteritems():
				if object.__class__ == moduleBrowser.Function:
					if not member.startswith("_"):
						functions[member] = [".. autofunction:: {0}\n".format(member)]
				elif object.__class__ == moduleBrowser.Class:
					classes[member] = [".. autoclass:: {0}\n".format(member),
									   "	:show-inheritance:\n",
									   "	:members:\n"]
				elif object.__class__ == moduleBrowser.Global:
					if not member.startswith("_"):
						moduleAttributes[member] = [".. attribute:: {0}.{1}\n".format(module, member)]

			moduleAttributes and rstFile.content.append("Module Attributes\n-----------------\n\n")
			for moduleAttribute in moduleAttributes.itervalues():
				rstFile.content.extend(moduleAttribute)
				rstFile.content.append("\n")

			functions and rstFile.content.append("Functions\n---------\n\n")
			for function in functions.itervalues():
				rstFile.content.extend(function)
				rstFile.content.append("\n")

			classes and rstFile.content.append("Classes\n-------\n\n")
			for class_ in classes.itervalues():
				rstFile.content.extend(class_)
				rstFile.content.append("\n")

			rstFile.write()
			modules.append(module)

		packagesModules["apiModules"].extend([module for module in modules if not "tests" in module])
		packagesModules["testsModules"].extend([module for module in modules if "tests" in module])

	apiFile = File("{0}{1}".format(output, FILES_EXTENSION))
	apiFile.content.extend(TOCTREE_TEMPLATE_BEGIN)
	for module in packagesModules["apiModules"]:
		apiFile.content.append("   {0} <{1}>\n".format(module, "api/{0}".format(module)))
	for module in packagesModules["testsModules"]:
		apiFile.content.append("   {0} <{1}>\n".format(module, "api/{0}".format(module)))
	apiFile.content.extend(TOCTREE_TEMPLATE_END)
	apiFile.write()

	return True

def getCommandLineArguments():
	"""
	Retrieves command line arguments.

	:return: Namespace.
	:rtype: Namespace
	"""

	parser = argparse.ArgumentParser(add_help=False)

	parser.add_argument("-h",
						"--help",
						action="help",
						help="'Displays this help message and exit.'")

	parser.add_argument("-p",
						"--packages",
						dest="packages",
						nargs="+",
						help="'Packages to include in the API.'")

	parser.add_argument("-i",
						"--input",
						type=unicode,
						dest="input",
						help="'Input modules directory.'")

	parser.add_argument("-o",
						"--output",
						type=unicode,
						dest="output",
						help="'Output reStructuredText files directory.'")

	parser.add_argument("-s",
						"--sanitizer",
						type=unicode,
						dest="sanitizer",
						help="'Sanitizer python module'")

	parser.add_argument("-x",
						"--excludedModules",
						dest="excludedModules",
						nargs="*",
						help="'Excluded modules.'")

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
	args.sanitizer = args.sanitizer if foundations.common.pathExists(args.sanitizer) else SANITIZER
	args.excludedModules = args.excludedModules if all(args.excludedModules) else []
	return buildApi(args.packages,
					args.input,
					args.output,
					args.sanitizer,
					args.excludedModules)

if __name__ == "__main__":
	main()
