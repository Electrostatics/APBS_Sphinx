# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python ff=unix noet sts=0 sw=4 ts=4 :
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
from asyncio import coroutine, Queue

import simplejson as json
from functools import partial

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

	# Type manager handle
	_tm = None

	def __init__(self, runner, plugins, source = None):
		'''Ctor
		This method _must_ be called with the event loop from which it will be
		called in the future, e.g., asyncio.get_event_loop().
		'''
		self._sinks = []

		# Retain a pointer to our source, and add ourself to it's list of sinks.
		self._source = source
		if source:
			source._sinks.append(self)

		# Producer/consumer queue
		self._queue = Queue()

		self.runner = runner
		self._plugins = plugins

		# create_task schedules the execution of the coroutine "run", wrapped
		# in a future.
		self._task = self.runner.create_task(self.run())


	def __getattr__(self, name):
		'''Plugin Pipeline Bulding
		This method is called when Python can't find a requested attribute. We
		use it to create a new plugin instance to add to the pipeline.
		'''
		if name in self._plugins:
			return partial(self._plugins[name], source = self)

		else:
			raise AttributeError

	@coroutine
	def publish(self, data):
		'''Publish data
		Called by a plugin to publish data to it's sinks.
		'''
		# Turn the data dict into a JSON string before sending it.  This may
		# not make a lot of sense yet, but eventually serialization for
		# transport will be essential.
		for sink in self._sinks:
			yield from sink._queue.put(json.dumps(data))


	@coroutine
	def read_data(self):
		'''Read data from queue
		Called by plugins to get data from their sources.
		'''
		data = yield from self._queue.get()
		return json.loads(data)


	@coroutine
	def done(self):
		'''The plugin is finished
		Called by a plugin to indicate to it's sinks that it has no more data.
		'''
		yield from self.publish(None)


	@classmethod
	def sinks(cls):
		'''Sink types
		These are an array of types that we sink, i.e., read.
		'''
		return []


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
		cls._tm = db._typemgr


	@classmethod
	def script_name(cls):
		'''Return the plug-in's script name.
		The script name is how the plug-in is referred to by command scripts.
		'''
		pass


	@abstractmethod
	@coroutine
	def run(self):
		'''Our main method where work is done
		This is the method that will be invoked when the plug-in needs to do
		some work.
		'''
		pass
