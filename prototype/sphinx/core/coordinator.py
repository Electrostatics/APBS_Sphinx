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

import os
import asyncio
import logging
from importlib import import_module
from functools import partial

from concurrent.futures import ProcessPoolExecutor

from sphinx.databus import SDBController

__all__ = ['Coordinator']

__author__ = 'Keith T. Star <keith@pnnl.gov>'

_log = logging.getLogger()

class Coordinator:
	'''Sphinx Main Runner-thing
	'''
	def __init__(self, plugins):
		self._plugin_dir = plugins
		self._plugins = {}
		self._plugin_funcs = {}
		self._databus = None
		self._loop = None
		self._tasks = []


	def start(self, cmd_file, cmd_args):
		'''Main entry point -- post constructor.
		cmd_file is the command file to process
		cmd_args are the arguments for the cmd file
		'''
		# Get a handle to our event loop.
		if os.name == 'nt':
			self._loop = asyncio.ProactorEventLoop()
			asyncio.set_event_loop(loop)
		else:
			self._loop = asyncio.get_event_loop()

		self._executor = ProcessPoolExecutor()
		self._loop.set_default_executor(self._executor)

		self._databus = SDBController()
		self._load_plugins()

		print("Ctrl-C to escape...")

		locals = dict([(p[0], p[1]) for p in [x.split('=') for x in cmd_args]])

		try:
			# Load and process the command file.  It's just Python.
			_log.info("Reading command file.")
			with open(cmd_file) as cf:
				code = compile(cf.read(), cmd_file, 'exec')
				exec(code, self._plugin_funcs, {'params':locals})

			_log.info("Starting the run loop.")
			self._loop.run_until_complete(asyncio.wait(self._tasks))

		except KeyboardInterrupt:
			pass

		except Exception:
			print("Oops -- something bad happened.  Check io.mc for details")

		finally:
			self.stop()


	def stop(self):
		self._executor.shutdown()
		self._loop.stop()
		self._loop.close()
		_log.info("The run loop is shut down.")


	@asyncio.coroutine
	def run_as_process(self, func, args):
		try:
			results = yield from self._loop.run_in_executor(self._executor, func,
					args)
		except:
			_log.info("We encountered an exception.  Goodbye.")
			self.stop()

		return results


	def create_task(self, func):
		task = self._loop.create_task(func)

		self._tasks.append(task)

		return task


	def _load_plugins(self):
		'''Load the plugins
		This implementation is näive and just loads everything.  We can clearly
		do better.
		'''
		print(os.getcwd())
		for file in os.listdir(self._plugin_dir):
			if os.path.isdir(os.path.join(self._plugin_dir, file)):
				# For now I'm thinking that we'll require the plug-in author to
				# put their plug-in in a file called plugin.py, inside of a
				# module that is named the same as their class implementation in
				# the plugin.py file.
				plugin = getattr(import_module(self._plugin_dir + '.' + file +
					'.plugin'), file)
				self._plugins[file] = plugin
				self._databus.add_plugin(plugin)

				# TODO: This is pretty lame, but it's a quick and dirty way to
				# see how this script thing is going to work out.
				self._plugin_funcs[plugin.script_name()] = partial(plugin,
					runner = self, plugins = self._plugin_funcs)
