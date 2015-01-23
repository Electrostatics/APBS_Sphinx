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

from abc import ABCMeta, abstractmethod
from asyncio import coroutine

__all__ = ['BasePlugin']

__author__ = 'Keith T. Star <keith@pnnl.gov>'

class BasePlugin(metaclass=ABCMeta):
	'''Core plug-in functionality
	A Sphinx plug-in needs to provide a minimim set of services in order to be
	useful.  Those are defined here, with default implementations where it
	makes sense.
	'''

	# This is a handle to the data bus.  It's set when we are registered.
	_databus = None

	def __init__(self, loop):
		'''Ctor
		This method _must_ be called with the event loop from which it will be
		called in the future, e.g., asyncio.get_event_loop().
		'''
		self._task = None
		self._loop = loop


	@classmethod
	def sinks(cls):
		'''Sink types
		These are an array of types that we sink, i.e., read.
		'''
		return []

	def feed(self, data):
		'''Feed a source.
		This method is called on an instance of a plug-in in order to give it
		data.
		'''
		pass


	def consume(self):
		'''
		'''


	@classmethod
	def sources(cls):
		'''Source types
		These are an array of types that we source, i.e., write.
		'''
		return []


	@classmethod
	def set_databus(cls, db):
		'''A handler to the Semantic Databus
		This gets set when the plug-in is registered.
		'''
		cls._databus = db


	@abstractmethod
	@coroutine
	def run(self):
		'''Our main method where work is done
		This is the method that will be invoked when the plug-in needs to do
		some work.
		'''
		pass


	def start(self):
		'''Start the plug-in
		This method should be called to start the plug-in by whomever set up
		the asyncio event loop.
		'''
		self._task = self._loop.create_task(self.run())
