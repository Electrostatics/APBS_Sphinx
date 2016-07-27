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

import io
from jsonschema import validate, ValidationError
import os
import simplejson as json

import logging

__all__ = ['OptionHandler', 'InvalidOrMissingOptionError', 'TooManyOptionsError',
           'InvalidOptionTypeError']

__author__ = 'Keith T. Star <keith@pnnl.gov>'

_log = logging.getLogger()

OPTION_SCHEMA_FILE = os.path.join(os.path.dirname(__file__), 'option_schema.json')
with open(OPTION_SCHEMA_FILE) as f:
    _option_schema = json.loads(f.read())


_type_map = {'bool': bool,
             'int': int,
             'float': float,
             'string': str}
    

class OptionHandler():
    def __init__(self, schema):
        if isinstance(schema,  str):
            schema = json.loads(schema)

        elif isinstance(schema, io.IOBase):
            schema = json.loads(schema.read())

        try:
            validate(schema, _option_schema)

        except ValidationError:
            _log.error('Plugin option validation error.')
            raise

        self._schema = schema

        self._var_types = {}
        self._misc_data = {}
        self._validation_dict = self._build_validator(schema)
        _log.debug(json.dumps(self._validation_dict, sort_keys=True, indent=4 * ' '))


    def validate(self, opts):
        return self._validate(self._validation_dict, opts)


    def get_misc(self, var):
        return self._misc_data[var]


    def _build_validator(self, schema):
        """Generate Validator
        
        Generate a validation dictionary that recognizes a valid set of options,
        given the provided schema.

        There are three different ways to group options, and each requires a
        different check.  The "one" group indicates that only a single option
        from a group may be indicated.  The "all" group signals that every 
        option in the group must be present .  Finally, "any", which is the 
        default grouping if no other group option is indicated, means that 
        zero or more options are required to be present.

        Finally, each user option is type checked against the schema.
        """
        vd = {'all': [], 'one': [], 'any': []}

        for s in schema:
            if 'all' in s.keys():
                for a in s['all']['options']:
                    if 'var' in a.keys():
                        v = a['var']
                        t = a['type']
                        if t == 'enum':
                            t = a['allowedValues']
                            self._var_types[v] = t

                        else:
                            self._var_types[v] = _type_map[t]


                        if 'misc' in a.keys():
                            self._misc_data[v] = a['misc']

                            
                        vd['all'].append(a['var'])
                        
                    else:
                        vd['all'].append(self._build_validator([a]))

            elif 'one' in s.keys():
                for o in s['one']['options']:
                    if 'var' in o.keys():
                        v = o['var']
                        t = o['type']
                        if t == 'enum':
                            t = o['allowedValues']
                            self._var_types[v] = t

                        else:
                            self._var_types[v] = _type_map[t]

                        if 'misc' in o.keys():
                            self._misc_data[v] = o['misc']

                            
                        vd['one'].append(o['var'])

                    else:
                        vd['one'].append(self._build_validator([o]))

            elif 'any' in s.keys():
                vd['any'].append(self._build_validator(s['any']['options']))

            else:
                v = s['var']
                t = s['type']
                if t == 'enum':
                    t = s['allowedValues']
                    self._var_types[v] = t

                else:
                    self._var_types[v] = _type_map[t]

                if 'misc' in s.keys():
                    self._misc_data[v] = s['misc']

                            
                vd['any'].append(s['var'])

        return vd


    def _validate(self, vd, opts):
        _log.debug('_validate\nvd is {}\nopts are {}'.format(vd, opts))
        # First test that all of the required opts are specified.
        for k in vd['all']:
            if isinstance(k, dict):
                if not self._validate(k, opts):
                    return False

            else:
                if k not in opts.keys():
                    err_str = "Expected option '{}' not found.".format(k)
                    _log.error(err_str)
                    raise InvalidOrMissingOptionError(err_str)

                else:
                    if type(opts[k]) != self._var_types[k]:
                        self._check_value_type(k, opts[k])


        # Next ensure that any mutually exclusive options are only specified
        # once.
        if vd['one']:
            found = False
            for k in vd['one']:
                if isinstance(k, dict):
                    try:
                        self._validate(k, opts)
                        if found:
                            err_str = "Option '{}' specified, but '{}' already processed.".format(found, k)
                            _log.error(err_str)
                            raise TooManyOptionsError(err_str)

                        found = k
                        
                    except InvalidOrMissingOptionError:
                        pass
                

                else:
                    if k in opts.keys():
                        if found:
                            err_str = "Option '{}' specified, but '{}' already processed.".format(found, k)
                            _log.error(err_str)
                            raise TooManyOptionsError(err_str)

                        else:
                            found = k
                            if type(opts[k]) != self._var_types[k]:
                                self._check_value_type(k, opts[k])

            if not found:
                err_str = "Expected option '{}' not found.".format(k)
                _log.error(err_str)
                raise InvalidOrMissingOptionError(err_str)

        # Finally, check the optional "any" options.
        if vd['any']:
            for k in vd['any']:
                if isinstance(k, dict):
                    self._validate(k, opts)

                else:
                    if k in opts.keys():
                        self._check_value_type(k, opts[k])

        return True


    def _check_value_type(self, var, value):
        var_type = self._var_types[var]
        if type(var_type) == list:
            if value not in var_type:
                err_str = "'Expected one of {} for enum '{}' and found '{}'.".format(var_type,
                                                                                     var,
                                                                                     value)
                _log.error(err_str)
                raise InvalidOptionTypeError(err_str)

        else:
            if var_type != type(value):
                err_str = "Value '{}' for variable '{}' is of type '{}', and should be '{}'.".format(value,
                                                                                                    var,
                                                                                                    type(value),
                                                                                                    var_type)
                _log.error(err_str)
                raise InvalidOptionTypeError(err_str)
        
            

class InvalidOrMissingOptionError(Exception):
    pass


class TooManyOptionsError(Exception):
    pass


class InvalidOptionTypeError(Exception):
    pass
