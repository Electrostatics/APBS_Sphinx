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

import logging
from functools import partial
import os
import re
import simplejson as json
import sys

from ..utils import *

__all__ = ['generate_types']

__author__ = 'Keith T. Star <keith@pnnl.gov>'

_log = logging.getLogger()

MODULE_DIR = os.path.dirname(__file__)
MMCIF_PDBX = os.path.join(MODULE_DIR, 'mmcif_pdbx_v40.dic')
SCHEMA_NAME = 'PDBxmmCIF.json'

def generate_types():
    generate_pdbx_mmcif_schema(os.path.join(MODULE_DIR, '../databus'))


def generate_pdbx_mmcif_schema(output_directory):
    '''Generate our base data types for atomic data.
    We use the PDBx/mmCIF schema dictionary from mmcif.wwpdb.org to generate
    code that we use with the databus, which allows for data interchange
    between our plugins.
    '''
    if not os.path.isdir(output_directory):
        _log.error('The output directory, "{}" in this case, is expected to '
                   'exist.'.format(output_directory))
        return

    # Open the schema file, and parse it's contents.
    dic_handle = open(MMCIF_PDBX)
    data = []
    dic = PdbxReader(dic_handle)
    dic.read(data)
    dic_handle.close()

    pdbx = load_schema(data)
    process_schema(pdbx)
    schema = gen_schema(pdbx, output_directory)

    schema_handle = open(os.path.join(output_directory, SCHEMA_NAME), 'w')
    schema_handle.write(schema)
    schema_handle.close()


def process_schema(pdbx):
    '''Fix links, etc.
    Process what we loaded from the PDBx/mmCIF parser so that we can 
    resolve item/property pointers.  And whatever else pops up.
    '''
    for id, item in pdbx['items'].items():
        if len(item['refs']) > 0:
            for ref in item['refs']:
                ref_item = pdbx['items'][ref]
                ref_item['type'] = 'ptr'
                ref_item['ptr'] = id[1:].replace('.', '/properties/')

def gen_schema(pdbx, uri):
    '''Generate the schema
    We'll be using a Python dict to hold our schema, and turn it into
    JSON using simplejson.
    '''
    schema = {
        '$schema': 'http://json-schema.org/draft-04/schema#',
        'id': 'file:/{}/{}'.format(uri, SCHEMA_NAME),
        'definitions': {},
        'properties': {},
        'type': 'object'
    }

    defs = schema['definitions']
    main_props = schema['properties']

    prop_count = 0
    for cat in pdbx['cats']:
        '''
        Create schema definitions for each category.
        '''
        defs[cat] = {
            'type': 'object',
            'properties': {},
            'required': [],
            'additionalProperties': False
        }
        # Add each category to the properties of the schema so that each may
        # be instantiated, and validated.
        main_props[cat] = {'$ref': '#/definitions/{}'.format(cat)}
        prop_count += 1

    for id, item in pdbx['items'].items():
        '''
        Create properties for the above definitions.
        '''
        item_id = item['item']
        cat = item['category']
        type = item['type']

        if type == 'ptr':
            defs[cat]['properties'][item_id] = {
                '$ref': '#/definitions/{}'.format(item['ptr'])
            }

        else:
            defs[cat]['properties'][item_id] = {'type': type}

        if item['required']:
            defs[cat]['required'].append(item_id)

    print("Imported {} JSON properties.".format(prop_count))
    
    return json.dumps(schema, sort_keys=True, indent=2 * ' ')


def load_schema(data):
    '''Load the schema using the given .cif file parser.
    It turns out that we can't properly process the information without having
    it loaded in memory first.  So that's what we do here.
    '''
    pdbx_dict = {'cats': [], 'items': {}}
    for block in data:
        if block.exists('category'):
            get = partial(get_prop_from_cat, block)
            id = get('category', 'id')
            pdbx_dict['cats'].append(id)

        elif block.exists('item'):
            # It's possible that 
            get = partial(get_prop_from_cat, block)
            name = block.getName()
            match = re.search('_(\w*)\.(.*)', name)
            cat_id = match.group(1)
            item_id = match.group(2)

            # This is as check to be sure that we are getting the matching
            # entry, since it's possible that there are multiple 'item'
            # rows.  Sheesh.
            item_name = get_item_name(get)
            assert(item_name == name)

            item_type = get_item_type(get)
            required = get_required(get)

            item_entry = {
                'item': item_id,
                'category': cat_id,
                'type': item_type,
                'required': required,
                'refs': []
            }
            
            if block.exists('item_linked'):
                # This means that there are items out there that are really
                # pointers to this one.  We'll need to collect those for later.
                links = block.getObj('item_linked')
                for i in range(links.getRowCount()):
                    item_entry['refs'].append(links.getValue('child_name', i))


            pdbx_dict['items'][name] = item_entry

        else:
            _log.info("found an unknown/unused block of type {}".format(block.getName()))

    return pdbx_dict


def get_item_type(getter):
    t = getter('item_type', 'code')
    if t == 'float':
        return 'number'
    elif t == 'int':
        return 'integer'
    else:
        return 'string'


def get_required(getter):
    req = getter('item', 'mandatory_code')
    if req == None or req == 'no':
        return False
    else:
        return True


def get_item_name(getter):
    name = getter('item', 'name')
    return name


def get_prop_from_cat(block, cat_name, prop_name):
    if not block.exists(cat_name):
        _log.debug('Passed block does not contain {} '
                   'category.'.format(cat_name))
        return None

    cat = block.getObj(cat_name)
    if not cat.hasAttribute(prop_name):
        _log.debug('Passed block does not contain {} '
                   'attribute.'.format(prop_name))
        return None

    return cat.getValue(prop_name)
