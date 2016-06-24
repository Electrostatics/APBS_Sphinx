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

from nose.tools import *

from functools import partial

from sphinx.plugin import *

__author__ = 'Keith T. Star <keith@pnnl.gov>'

def setup_runner():
    global runner
    runner = TestRunner()


@with_setup(setup_runner)
def test_impedence():
    '''Test Impedence Match

    Validate that impedence checking works ok when the source matches the sink.
    '''
    source = runner.load('source')
    assert_is_instance(source().sink(), SinkPlugin)


@with_setup(setup_runner)
@raises(ImpedenceMismatchError)
def test_impedence_fail():
    '''Test Impedence Mismatch

    Verify that the ImpedenceMismatchError is thrown when a source does not
    match the sink.
    '''
    sink = runner.load('sink')
    sink().source()


class TestRunner():
    def __init__(self):
        self._plugin_dict = {}

        self._plugin_dict = {'source': None, 'sink': None}
        self._plugin_dict['sink'] = partial(SinkPlugin, runner=self, plugins=self._plugin_dict)
        self._plugin_dict['source'] = partial(SourcePlugin, runner=self, plugins=self._plugin_dict)

    def load(self, plugin):
        return self._plugin_dict[plugin]
        
    def create_task(self, func):
        pass
        

class SourcePlugin(BasePlugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def sources(cls):
        return ['a_number'];

    def run(self):
        pass


class SinkPlugin(BasePlugin):
    def __init_(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def sinks(cls):
        return ['a_number']

    def run(self):
        pass
