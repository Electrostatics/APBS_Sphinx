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

from jsonschema import ValidationError

from sphinx.databus import TypeManager

__author__ = 'Keith T. Star <keith@pnnl.gov>'


# Just a few quick assertions to make sure that we are loading
# the PDBx/mmCIF schema.
def test_that_TM_loads_pdbx_mmcif():
    tm = TypeManager()
    at_schema = tm.get_schema('atom_type')
    assert_equal(type(at_schema), dict)
    assert_equal(at_schema['type'], 'object')
    assert_equal(at_schema['required'], ['symbol'])
    assert_equal(at_schema['properties']['symbol'],
                 {'type': 'string'})


def test_value_creation_with_kwargs():
    tm = TypeManager()
    at = tm.new_atom_type(symbol='C', radius_bond=1.1)
    assert_equal(at, {'atom_type': {'symbol': 'C', 'radius_bond': 1.1}})


def test_value_creation_with_dict():
    tm = TypeManager()
    at = tm.new_atom_type({'symbol': 'C', 'radius_bond': 1.1})
    assert_equal(at, {'atom_type': {'symbol': 'C', 'radius_bond': 1.1}})


@raises(AttributeError)
def test_no_such_type():
    tm = TypeManager()
    tm.new_fubar()


@raises(ValidationError)
def test_validation_missing_required():
    tm = TypeManager()
    at = tm.new_atom_type()


@raises(ValidationError)
def test_validation_extra_data():
    tm = TypeManager()
    at = tm.new_atom_type(radius=1.10)


@raises(ValidationError)
def test_validation_wrong_property_type():
    tm = TypeManager()
    at = tm.new_atom_type(symbol=7)


def test_new_type():
    tm = TypeManager()
    tm.define_type('apbs_type',
                   {
                    'width': {'type': 'number'},
                    'height': {'type': 'integer'},
                    'widgets': {
                        'type': 'array',
                        'items': {'$ref': '#/definitions/atom_type'}
                    }
                   })
    at = tm.new_apbs_type(width=1.24, height=7, widgets=[
                          {'symbol': 'C'},
                          {'symbol': 'O'}])

    value = at['apbs_type']
    assert_equal(value['width'], 1.24)
    assert_equal(value['height'], 7)
    assert_equal(value['widgets'][0], {'symbol': 'C'})
    assert_equal(value['widgets'][1], {'symbol': 'O'})


def test_extend_type():
    tm = TypeManager()
    tm.define_type('apbs_atom_type',
                   {'radius': {'type': 'number'}},
                   base='atom_type')
    at = tm.new_apbs_atom_type(symbol='O', radius=1.18)
