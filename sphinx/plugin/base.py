# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python ff=unix sw=4 ts=4 sts=4 et:
# APBS -- Adaptive Poisson-Boltzmann Solver
#
#  Nathan A. Baker (nathan.baker@pnnl.gov)
#  Pacific Northwest National Laboratory
#
#  Additional contributing authors listed in the code documentation.
#
# Copyright (c) 2010-2016 Battelle Memorial Institute. Developed at the
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
from asyncio import Queue
import logging

import simplejson as json
from functools import partial

__all__ = ['BasePlugin', 'ImpedenceMismatchError']

__author__ = 'Keith T. Star <keith@pnnl.gov>'

_log = logging.getLogger()

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
        '''Constructor

        This is how our plugin pipeline is constructed.  Each plugin instance
        is created when the input script is read, and they are chained together,
        from source to sink, here.

        This method _must_ be called with the event loop from which it will be
        called in the future, e.g., asyncio.get_event_loop().
        '''

        # A dict that maps each destination for our data, to the type that the
        # destination can consume.
        self._sinks = {}

        # Retain a pointer to our source, and add ourself to it's list of sinks.
        self._source = source
        if source:
            # Validate that we can process data from this source
            sink_types = set(source.sources()).intersection(self.sinks())
            if len(sink_types):
                source._set_sink(self, sink_types.pop())

            else:
                err = "{} cannot sink '{}'".format(self, source.sources())
                _log.error(err)
                raise ImpedenceMismatchError(err)

        # Our input queue
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


    def _set_sink(self, sink, data_type):
        '''Register a sink

        Called during initialization to register a sink (destination for our
        output).
        '''
        self._sinks[sink] = data_type


    async def publish(self, data):
        '''Publish data

        Called by a plugin to publish data to it's sinks.
        '''
        for sink, data_type in self._sinks.items():
            # Special case 'None', since that's our 'eof'.  See the 'done'
            # method below.
            if data:
                data = self.xform_data(data, data_type)
            await self._databus.publish(data, sink)


    async def write_data(self, data):
        '''Write data to queue

        Called by the databus controller to enqueue data from our source.
        '''
        await self._queue.put(data)


    async def read_data(self):
        '''Read data from queue

        Called by plugins to get data from their sources.
        '''
        payload = await self._queue.get()
        return payload



    async def done(self):
        '''The plugin is finished

        Called by a plugin to indicate to it's sinks that it has no more data.
        '''
        # TODO: It feels clumsy to use getting "None" as "EOT".  Also, it
        # requires that the plugins test for it to stop reading data.
        await self.publish(None)



    # Sources and sinks, oh my!  These follow the current flow analogy.
    # Data flows from a source to a sink.  Our input comes from a source,
    # and we sink it, process the data in some manner, and then source
    # it to the next plugin in the pipeline.
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
    def xform_data(self, data, to_type):
        '''Transform data to a specific type

        This method must be able to transform the input, 'data', to the 'to_type'.
        The plugin will only be responsible for transforming types that are
        specified in our "sources" method.

        There is no expectation on how the plugin represents 'data', but it would
        make sense to do so in some manner that is not only natural for the plugin,
        but also easily transformed.
        '''
        pass



    @abstractmethod
    async def run(self):
        '''Our main method where work happens

        This is the method that will be invoked when the plug-in needs to do
        some work.
        '''
        pass


class ImpedenceMismatchError(Exception):
    pass
