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

from jsonschema import validate, ValidationError
import simplejson as json
from functools import partial
import os
import re

import logging

__all__ = ['TypeManager']

__author__ = 'Keith T. Star <keith@pnnl.gov>'

_log = logging.getLogger()


PDBx_mmCIF_SCHEMA = os.path.join(os.path.dirname(__file__), './PDBxmmCIF.json')

class TypeManager:
    '''Type Manager
    This is the guy that handles everything to do with types in the databus.
    Plugins come here to create instances of data for the databus.  They may
    also extend existing types here or create entirely new types.
    '''
    def __init__(self):
        # Load the PDBx/mmCIF schemea
        with open(PDBx_mmCIF_SCHEMA) as f:
            self._schema = json.loads(f.read())

        # Setup a regex for "new_*" method dispatching.  What's "new_*" method
        # dispatching you ask?  Check it out below in the __getattr__ method.
        self._method_regex = re.compile('new_(.*)')

    
    def get_schema(self, key):
        return self._schema['definitions'][key]
    
    
    def __getattr__(self, name):
        ''' Implement hook for new_* methods
        Here we use the old __getattr__ trick to make it easy to create a new
        instance of a type.  Say we have a type called "apbs_atom" (which we do),
        and we'd like to create one.  Given an instance of a TypeManager, e.g.,
        tm, this trick let's us call tm.new_apbs_atom() to create that instance
        we want.
        However, this is really only a hook to return a partially bound instance
        of a _new_value function that actually does the hard work.
        '''
        method = self._method_regex.match(name).group(1)
        if method in self._schema['properties']:
            return partial(self._new_value, method)

        else:
            _log.error('Unknown type: {}'.format(method))
            raise AttributeError


    def _new_value(self, method, value_dict=None, **kwargs):
        ''' Actually implement the new_* methods
        Nothing too tricky going on here.  We just create a valid instance of a
        JSON schema value, either from a dictionary or kwargs.  Note that we
        validate the value after we create it.
        '''
        d = {method: {}}
        if value_dict and type(value_dict) == dict:
            d[method] = value_dict

        else:
            for k, v in kwargs.items():
                d[method][k] = v

        #TODO: (NB) I'm concerned that this may be too slow.
        try:
            validate(d, self._schema)
        except ValidationError:
            _log.error('Validation Error: {}'.format(d))
            raise

        return d


    def define_type(self, name, properties, base=None):
        '''Define a new type
        Allow for new types of values to be created and inserted into the
        pipeline.
        '''
        #TODO: perhaps create a self._user_schema to hold these?
        #TODO: allow user to specify required properties

        if base and base in self._schema['definitions']:
            new_type = self._schema['definitions'][name] = self._schema['definitions'][base]
            for k, v in properties.items():
                new_type['properties'][k] = v

        else:
            new_type = self._schema['definitions'][name] = {}
            new_type['type'] = 'object'
            new_type['properties'] = properties
            new_type['additionalProperties'] = False

        # Add the type to the properties dict
        self._schema['properties'][name] = {'$ref':
            '#/definitions/{}'.format(name)}
