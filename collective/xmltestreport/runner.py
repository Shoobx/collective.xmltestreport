##############################################################################
#
# Copyright (c) 2004-2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test runner based on zope.testing.testrunner
"""
import os
import sys
import optparse

try:
    from zope.testrunner.runner import Runner
    from zope.testrunner.options import parser
except ImportError:
    from zope.testing.testrunner.runner import Runner
    from zope.testing.testrunner.options import parser


from collective.xmltestreport.formatter import XMLOutputFormattingWrapper

# Set up XML output parsing

xmlOptions = optparse.OptionGroup(parser, "Generate XML test reports",
    "Support for JUnit style XML output")
xmlOptions.add_option(
    '--xml', action="store_true", dest='xmlOutput',
    help="""\
If given, XML reports will be written to the current directory. If you created
the testrunner using the buildout recipe provided by this package, this will
be in the buildout `parts` directory, e.g. `parts/test`.
""")
xmlOptions.add_option(
    '--xml-setup-teardown', action="store_true", dest='xmlSetupTeardown',
    help="""\
If given, test setUp and tearDown runs will be also reported in the XML.
Current shortcoming is that suites are not supported, output is collapsed
into a `single.xml`.
""")
xmlOptions.add_option(
    '--xml-suite-name', action="store", dest='xmlOverrideSuiteName',
    help="""\
If given, overwrites testsuite names with the given string.
Handy to set a/the output xml filename.
""")

parser.add_option_group(xmlOptions)

# Test runner and execution methods


class XMLAwareRunner(Runner):
    """Add output formatter delegate to the test runner before execution
    """

    def configure(self):
        super(XMLAwareRunner, self).configure()
        so = self.options
        so.output = XMLOutputFormattingWrapper(
            so.output, cwd=os.getcwd())

        so.output.outputSetupTeardown = so.xmlSetupTeardown
        if so.xmlOverrideSuiteName:
            so.output.overrideSuiteName = so.xmlOverrideSuiteName


def run(defaults=None, args=None, script_parts=None):
    """Main runner function which can be and is being used from main programs.

    Will execute the tests and exit the process according to the test result.

    """
    failed = run_internal(defaults, args, script_parts=script_parts)
    sys.exit(int(failed))


def run_internal(defaults=None, args=None, script_parts=None):
    """Execute tests.

    Returns whether errors or failures occured during testing.

    """

    runner = XMLAwareRunner(defaults, args, script_parts=script_parts)
    try:
        runner.run()
    finally:
        # Write XML file of results if -x option is given
        if runner.options.xmlOutput:
            runner.options.output.writeXMLReports()

    return runner.failed
