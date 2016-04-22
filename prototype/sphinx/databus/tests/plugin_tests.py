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

from sphinx.databus import SDBController
from sphinx.plugin import BasePlugin

__author__ = 'Keith T. Star <keith@pnnl.gov>'

def setup_plugins():
    global databus

    databus = SDBController()

    # This is digging in the guts of the controller, and currently there's no
    # interface to add types.  However, for a test, I don't think that this
    # is too terrible.
    databus._typemgr.define_type('type1', {'datum': { 'type': 'number'}})
    databus._typemgr.define_type('type2', {'datum': { 'type': 'string'}})
    databus._typemgr.define_type('type3', {'datum': { 'type': 'boolean'}})
    
    databus.add_plugin(TestPlugin)
    databus.add_plugin(SymmetricTestPlugin)
    databus.add_plugin(UberPlugin)


@with_setup(setup_plugins)
def test_add_plugin():
    # Test that the sources are properly captured.
    type1_sources = databus.sources_for('type1')
    assert_equal(2, len(type1_sources))
    assert_in(TestPlugin, type1_sources)
    assert_in(UberPlugin, type1_sources)

    type2_sources = databus.sources_for('type2')
    assert_equal(2, len(type2_sources))
    assert_in(SymmetricTestPlugin, type2_sources)
    assert_in(UberPlugin, type2_sources)

    type3_sources = databus.sources_for('type3')
    assert_equal(2, len(type3_sources))
    assert_in(SymmetricTestPlugin, type3_sources)
    assert_in(UberPlugin, type3_sources)
    
    # Test that the sinks are properly captured.
    type1_sinks = databus.sinks_for('type1')
    assert_equal(2, len(type1_sinks))
    assert_in(SymmetricTestPlugin, type1_sinks)
    assert_in(UberPlugin, type1_sinks)
    
    type2_sinks = databus.sinks_for('type2')
    assert_equal(2, len(type2_sinks))
    assert_in(TestPlugin, type2_sinks)
    assert_in(UberPlugin, type2_sinks)
    
    type3_sinks = databus.sinks_for('type3')
    assert_equal(2, len(type3_sinks))
    assert_in(TestPlugin, type3_sinks)
    assert_in(UberPlugin, type3_sinks)


class TestPlugin(BasePlugin):
    '''Super simple plugin that has sources and sinks
    '''
    def __init__(self):
        super().__init__()

    @classmethod
    def sinks(cls):
        return ['type2', 'type3']

    @classmethod
    def sources(cls):
        return ['type1']

    def run(self):
        pass

    
class SymmetricTestPlugin(BasePlugin):
    '''Super simple plugin that is symmetric to TestPlugin
    '''
    def __init__(self):
        super().__init__()

    @classmethod
    def sinks(cls):
        return ['type1']

    @classmethod
    def sources(cls):
        return ['type2', 'type3']

    def run(self):
        pass


class UberPlugin(BasePlugin):
    '''We do it all -- if not very well.
    '''
    def __init__(self):
        super().__init__()

    @classmethod
    def sinks(cls):
        return ['type1', 'type2', 'type3']

    @classmethod
    def sources(cls):
        return ['type1', 'type2', 'type3']

    def run(self):
        pass
