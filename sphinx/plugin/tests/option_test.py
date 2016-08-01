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
import os
import simplejson as json

from sphinx.plugin import *

__author__ = 'Keith T. Star <keith@pnnl.gov>'


# Setup functions
def init_handler():
    global handler
    with open(os.path.join(os.path.dirname(__file__), 'test_schema.json')) as f:
        handler = OptionHandler(f)


def init_simple_all():
    global handler
    test = [{
        'all': {
            'options':[
                {
                    'name': 'foo',
                    'var': 'foo',
                    'type': 'bool'
                },
                {
                    'name': 'bar',
                    'var': 'bar',
                    'type': 'string'
                }
            ]
        }
    }]

    handler = OptionHandler(json.dumps(test))


def init_simple_one():
    global handler
    test = [{
        'one': {
            'options':[
                {
                    'name': 'foo',
                    'var': 'foo',
                    'type': 'bool'
                },
                {
                    'name': 'bar',
                    'var': 'bar',
                    'type': 'string'
                }
            ]
        }
    }]

    handler = OptionHandler(json.dumps(test))


def init_all_under_one():
    global handler
    test = [{
        'one': {
            'options': [
                {
                    'name': 'alpha',
                    'var': 'alpha',
                    'type': 'int'
                },
                {
                    'name': 'beta',
                    'var': 'beta',
                    'type': 'enum',
                    'allowedValues': ['one', 'two', 'three']
                },
                {
                    'all': {
                        'options':[
                            {
                                'name': 'foo',
                                'var': 'foo',
                                'type': 'bool'
                            },
                            {
                                'name': 'bar',
                                'var': 'bar',
                                'type': 'string'
                            }
                        ]
                    }
                }
            ]
        }
    }]

    handler = OptionHandler(json.dumps(test))


def init_one_under_all():
    global handler
    test = [{
        'all': {
            'options': [
                {
                    'name': 'alpha',
                    'var': 'alpha',
                    'type': 'int'
                },
                {
                    'name': 'beta',
                    'var': 'beta',
                    'type': 'enum',
                    'allowedValues': ['one', 'two', 'three']
                },
                {
                    'one': {
                        'options':[
                            {
                                'name': 'foo',
                                'var': 'foo',
                                'type': 'bool'
                            },
                            {
                                'name': 'bar',
                                'var': 'bar',
                                'type': 'string'
                            }
                        ]
                    }
                }
            ]
        }
    }]

    handler = OptionHandler(json.dumps(test))


# Initialization Tests
def test_init_with_array():
    test = [
        {
            'name': 'opt',
            'var': '--opt',
            'type': 'bool'
        }
    ]

    OptionHandler(test)


def test_init_with_string():
    test = [
        {
            'name': 'opt',
            'var': '--opt',
            'type': 'bool'
        }
    ]

    OptionHandler(json.dumps(test))


@raises(ValidationError)
def test_bad_schema():
    OptionHandler({})


def test_init_with_file():
    with open(os.path.join(os.path.dirname(__file__), 'test_schema.json')) as f:
        OptionHandler(f)


def test_init_with_file_path():
    OptionHandler(os.path.join(os.path.dirname(__file__), 'test_schema.json'))

    

# Validation Tests
@raises(InvalidOrMissingOptionError)
@with_setup(init_simple_all)
def test_fail_on_empty_opts():
    handler.validate({})


@with_setup(init_simple_all)
def test_simple_all_success():
    assert_true(handler.validate({'foo': True, 'bar': 'baz'}))


@with_setup(init_simple_all)
@raises(InvalidOrMissingOptionError)
def test_simple_all_missing_option():
    handler.validate({'foo': True})

    
@with_setup(init_simple_one)
def test_simple_one_success():
    assert_true(handler.validate({'foo': True}))


@with_setup(init_simple_one)
@raises(TooManyOptionsError)
def test_simple_one_too_many_options():
    handler.validate({'foo': True, 'bar': 'baz'})


@with_setup(init_all_under_one)
def test_all_under_one_success():
    assert_true(handler.validate({'alpha': 7}))
    assert_true(handler.validate({'beta': 'one'}))
    assert_true(handler.validate({'foo': True, 'bar': 'false'}))
    

@with_setup(init_all_under_one)
@raises(TooManyOptionsError)
def test_all_under_one_too_many_options():
    handler.validate({'alpha': 6, 'foo': True, 'bar': 'false'})
    

@with_setup(init_all_under_one)
@raises(InvalidOrMissingOptionError)
def test_all_under_one_missing_options():
    handler.validate({'foo': False})
    

@with_setup(init_one_under_all)
def test_one_under_all_success():
    assert_true(handler.validate({'alpha': 6, 'beta': 'one', 'foo': True}))
    assert_true(handler.validate({'alpha': 6, 'beta': 'two', 'bar': 'false'}))
    

@with_setup(init_one_under_all)
@raises(TooManyOptionsError)
def test_one_under_all_too_many_options():
    handler.validate({'alpha': 6, 'beta': 'three', 'foo': True, 'bar': 'false'})
    

@with_setup(init_one_under_all)
@raises(InvalidOrMissingOptionError)
def test_one_under_all_missing_options():
    handler.validate({'foo': False})
    

@with_setup(init_handler)
def test_successful_validation():
    assert_true(handler.validate({'userff': 'foo', 'usernames': 'bar'}))
    assert_true(handler.validate({'ff': 'amber'}))


@with_setup(init_handler)
def test_floating_options_and_any():
    assert_true(handler.validate({'clean': True, 'help': True, 'chain': True}))


@with_setup(init_handler)
@raises(InvalidOrMissingOptionError)
def test_fail_on_incomplete_all():
    handler.validate({'userff': 'foo'})


@with_setup(init_handler)
@raises(InvalidOptionTypeError)
def test_wrong_option_type():
    handler.validate({'userff': 7, 'usernames': 'bar'})


@with_setup(init_handler)
@raises(InvalidOptionTypeError)
def test_invalid_enum():
    handler.validate({'ff': 'foo'})


@with_setup(init_handler)
def test_misc_data():
    m = handler.get_misc('ff')
    assert_equal(m['cmd_opt'], "--ff={}")
    m = handler.get_misc('nodebump')
    assert_equal(m['cmd_opt'], "--nodebump")


