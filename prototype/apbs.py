#!/usr/bin/env python3
# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4
# APBS -- Adaptive Poisson-Boltzmann Solver
#
#  Nathan A. Baker (nathan.baker@pnnl.gov)
#  Pacific Northwest National Laboratory
#
#  Additional contributing authors listed in the code documentation.
#
# Copyright (c) 2010-2015 Battelle Memorial Institute. Developed at the
# Pacific Northwest National Laboratory, operated by Battelle Memorial
# Institute, Pacific Northwest Division for the U.S. Department of Energy.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# Neither the name of the developer nor the names of its contributors may be
# used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
#}}}

import sys
import os
import logging
import argparse
import asyncio

from sphinx.core import Coordinator

PLUGIN_DIR = "plugins"

__author__ = 'Keith T. Star <keith@pnnl.gov>'

# I'm not at all convinced that we should continue with 'io.mc' and neither am I
# convinced that we shouldn't.
logging.basicConfig(filename='io.mc', level=logging.INFO,
	format='%(asctime)s %(message)s')

# TODO: log errors to stderr.
_log = logging.getLogger(os.path.basename(sys.argv[0]))


def parse_args():
	'''Parse command line arguments
	For now I'm not terribly concerned about dealing with a bunch of different
	options.  In fact, I think it would be best to keep them down in any case
	and relegate options to the command files.
	'''
	parser = argparse.ArgumentParser(description="APBS (sphinx)")
	parser.add_argument('command_file', metavar='cmd_file', nargs=1,
		help="file containing APBS commands, followed by it's arguments")
	parser.add_argument('cmd_args', nargs=argparse.REMAINDER)
	args = parser.parse_args()

	cmd = args.command_file[0]
	cmd_args = args.cmd_args
	_log.info('Command file: {}, args: {}'.format(cmd, cmd_args))

	return cmd, cmd_args


def main():
	try:
		_log.info('Hello world, from APBS (sphinx).')

		# Get files from the command line
		cmd, args = parse_args()

		# Create, and start the "Coordinator"
		Coordinator(PLUGIN_DIR).start(cmd, args)

	except Exception as e:
		_log.exception('Unhandled exception:')

if __name__ == '__main__':
	# Script entry point
	try:
		sys.exit(main())
	except KeyboardInterrupt:
		pass
