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

import asyncio
import logging

from sphinx.plugin import BasePlugin

__author__ = 'Keith T. Star <keith@pnnl.gov>'

_log = logging.getLogger()

def define_types(tm):
    '''Initialize Types
    Create type definitions for anthing that we source or sink, that isn't
    already defined by Sphinx Core.
    We are passed the TypeManager instance to use.
    '''
    # TODO: This should probably include the encoding, e.g., UTF-8, etc.
    # I'm not doing that now though because it opens a huge can of worms:
    # having to explicitly deal with character encodings, etc.
    tm.define_type('text',
                   {
                       'lines': {
                           'type': 'array',
                           'items': {'type': 'string'}
                       }
                   })


LINE_COUNT = 100

class ReadFile(BasePlugin):
    '''Plugin for reading a file
    This reads a text file, and yields a single line at a time.  We'll likely
    as not find that we need different sorts of readers.  The source type for
    this plugin should reflect the type of data that it produces.
    '''
    def __init__(self, file, **kwargs):
        super().__init__(**kwargs)

        self._file = file
        _log.info("ReadFile plug-in initialized.")


    @classmethod
    def script_name(cls):
        return "read_file"


    @classmethod
    def sinks(cls):
        return None


    @classmethod
    def sources(cls):
        return ['text']


    # I don't know that these are necessary, so much as they may prove to be
    # pedagogical.
    async def open(self):
        return open(self._file, 'r')

    async def read_lines(self, file):
        lines = []
        for c in range(LINE_COUNT):
            line = file.readline()

            if line == "":
                break

            lines.append(line)

        return lines


    async def run(self):
        # Note that we are opening and reading the file asynchronously.
        file = await self.open()
        lines = await self.read_lines(file)

        while lines:
            data = self._tm.new_text({'lines': lines})
            await self.publish(data)

            # This sleep allows subsequent plugins to start doing their
            # thing.
            await asyncio.sleep(0)

            lines = await self.read_lines(file)


        await self.done()
        file.close()


    def xform_data(self, data, to_type):
        return data
