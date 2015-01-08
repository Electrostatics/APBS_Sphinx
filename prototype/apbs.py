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
# Portions Copyright (c) 2002-2010, Washington University in St. Louis.
# Portions Copyright (c) 2002-2010, Nathan A. Baker.
# Portions Copyright (c) 1999-2002, The Regents of the University of
# California.
# Portions Copyright (c) 1995, Michael Holst.
# All rights reserved.
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
from importlib import import_module

import sphinx.databus

print(os.path.dirname(sphinx.databus.__file__))

PLUGIN_DIR = "plugins"

__author__ = 'Keith T. Star <keith@pnnl.gov>'

# I'm not at all convinced that we should continue with 'io.mc' and neither am I
# convinced that we shouldn't.
logging.basicConfig(filename='io.mc', level=logging.INFO,
	format='%(asctime)s %(message)s')
_log = logging.getLogger(os.path.basename(sys.argv[0]))

def parse_args():
	'''Parse command line arguments
	For now I'm not terribly concerned about dealing with a bunch of different
	options.  In fact, I think it would be best to keep them down in any case
	and relegate options to the command files.
	'''
	parser = argparse.ArgumentParser(description='APBS (sphinx)')
	parser.add_argument('command_files', metavar='cmd_file', nargs='+',
		type=argparse.FileType('r'), help='file containing APBS commands')
	parser.add_argument('-o', '--ontology', action='store_true',
		help='display the SDB ontology')
	args = parser.parse_args()
	files = [file.name for file in args.command_files]
	_log.info('Command files: {0}'.format(files))

	return files

def load_plugins(plugin_dir):
	'''Load the plugins for use
	This implementation is näive and just loads everything.  We can clearly do
	better.
	'''
	plugins = {}
	for file in os.listdir(plugin_dir):
		if os.path.isdir(os.path.join(plugin_dir, file)):
			plugins[file] = import_module(plugin_dir + '.' + file)

	return plugins


def main():
	try:
		_log.info('Hello world, from APBS (sphinx).')

		files = [os.path.splitext(file) for file in parse_args()]
		plugins = load_plugins(PLUGIN_DIR)

		print(files)
		print(plugins)

		loop = asyncio.get_event_loop()
		try:
			loop.run_until_complete()
		finally:
			loop.close()

	except Exception as e:
		_log.exception('Unhandled exception:')

if __name__ == '__main__':
	# Script entry point
	try:
		sys.exit(main())
	except KeyboardInterrupt:
		pass
