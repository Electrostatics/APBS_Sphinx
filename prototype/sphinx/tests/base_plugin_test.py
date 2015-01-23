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

from nose.tools import *

import asyncio

from sphinx.databus import SDBController
from sphinx.plugin import BasePlugin

__author__ = 'Keith T. Star <keith@pnnl.gov>'

def setup_simple_plugins():
	global databus, source, sink

	loop = asyncio.get_event_loop()

	databus = SDBController()
	databus.add_plugin(SimpleSourceTestPlugin)
	databus.add_plugin(SimpleSinkTestPlugin)

	source = SimpleSourceTestPlugin("This is a test string.", loop)
	sink = SimpleSinkTestPlugin(loop)

@with_setup(setup_simple_plugins)
def test_sdb_connection():
	assert_equal(databus, source._databus)
	assert_equal(databus, sink._databus)

@with_setup(setup_simple_plugins)
def test_read_from_source():
	pass

@with_setup(setup_simple_plugins)
def test_write_to_sink():
	pass

@with_setup(setup_simple_plugins)
def test_data_xfer():
	pass


class SimpleSourceTestPlugin(BasePlugin):
	'''Super simple plugin that acts as a data source
	'''
	def __init__(self, str, *args):
		super().__init__(*args)
		self._string = str

	@classmethod
	def sinks(cls):
		return []

	@classmethod
	def sources(cls):
		return [{'Type':'foo'}]

	def run(self):
		pass

	def run(self):
		pass

class SimpleSinkTestPlugin(BasePlugin):
	'''Super simple plugin that acts as a data sink
	'''
	def __init__(self, *args):
		super().__init__(*args)

	@classmethod
	def sinks(cls):
		return [{'Type':'foo'}]

	@classmethod
	def sources(cls):
		return []

	def run(self):
		pass
