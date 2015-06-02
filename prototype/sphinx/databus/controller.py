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

import logging

__all__ = ['SDBController']

__author__ = 'Keith T. Star <keith@pnnl.gov>'

_log = logging.getLogger()

class SDBController:
	'''Semantic Databus Controller
	This controller is the main point of contact for plug-ins to register
	themselves, and to request data from other plug-ins.
	'''
	def __init__(self):
		self._source_types = {}
		self._sink_types = {}


	def add_plugin(self, plugin):
		'''Plug-ins are registered here
		In order to use a plug-in with the databus it must be registered with
		the databus via this method.  Here we interrogate the plug-in for the
		types that it soures as well as sinks, and store that data with a
		reference to the plugin class.
		We also give the plug-in a reference to ourself so that it can request
		data.
		'''
		_log.info('Registering plug-in "{}" '.format(plugin.__name__) +
			'with sources {} '.format(plugin.sources()) +
			 'and sinks {}.'.format(plugin.sinks()))
		plugin.set_databus(self)

		for source in plugin.sources():
			self._get_plugin_list(source, self._source_types).append(plugin)

		for sink in plugin.sinks():
			self._get_plugin_list(sink, self._sink_types).append(plugin)


	def sources_for(self, type):
		'''Get plug-ins that grok a source.
		Return a list (array) of plug-ins that source the type argument.
		'''
		return self._get_plugin_list(type, self._source_types)


	def sinks_for(self, type):
		'''Get plug-ins that grok a sink
		'''
		return self._get_plugin_list(type, self._sink_types)

	def _get_plugin_list(self, key, dict):
		'''Return an array buried in a dictionary of semantic types
		Our lists of sink and source handlers are indexed by a hierarchy of
		keys where deeper levels are more specific instances of a type.
		A type can increase specificity by using slashes.
		'''
		# TODO: We need more than just 'Type' to justify a dict.  It's also
		# keeping us from doing something like:
		# 	{'Type': ['atom/elec', 'atom/apolar', 'text'] }
		type = key['Type'].split('/')
		first = type.pop(0)
		try:
			handlers = dict[first]
		except KeyError:
			dict[first] = handlers = {}

		for t in type:
			try:
				handlers = handlers[t]
			except KeyError:
				handlers[t] = handlers = {}

		try:
			plugins = handlers['__plugins__']
		except KeyError:
			handlers['__plugins__'] = plugins = []

		return plugins
