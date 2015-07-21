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
from functools import partial
import os
import re
import simplejson as json
import sys

from utils import *

__all__ = ['do_it']

__author__ = 'Keith T. Star <keith@pnnl.gov>'

_log = logging.getLogger()

MMCIF_PDBX = os.path.join(os.path.dirname(__file__), 'mmcif_pdbx_v40.dic')
SCHEMA_NAME = 'PDBxmmCIF.json'

def do_it(output_directory):
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

	cats = get_categories(data)
	schema = gen_schema(cats)

	schema_handle = open(os.path.join(output_directory, SCHEMA_NAME), 'w')
	schema_handle.write(schema)
	schema_handle.close()


def gen_schema(categories):
	'''Generate the schema
	We'll be using a Python dict to hold our schema, and turn it into
	JSON using simplejson.
	'''
	schema = {
		'$schema': 'http://json-schema.org/draft-04/schema#',
		'id': 'http://mmcif.wwpdb.org/' + SCHEMA_NAME,
		'definitions': {}
	}

	defs = schema['definitions']
	for cat_def in categories:
		name = cat_def['name']
		cat = defs[name] = {'type': 'object', 'properties': {}, 'required': []}

		req = cat['required']
		props = cat['properties']
		for prop in cat['properties']:
			
		

	return json.dumps(schema, sort_keys=True, indent=2 * ' ')


def get_categories(data):
	# Now we rip through the data blocks looking for 'categories', which
	# contain 'items'.  A category can be roughly mapped to a class and
	# it's items map to class member variables.
	categories = {}
	for block in data:
		if block.exists('category'):
			get = partial(get_prop_from_cat, block)
			new_cat = {'name': get('category', 'id'),
				# Yuk.
				'key': re.search('\w*\.(.*)', get('category_key', 'name')).group(1),
				'properties': {}}

			categories[new_cat['name']] = new_cat

		elif block.exists('item'):
			get = partial(get_prop_from_cat, block)
			name = get_item_name(get)
			cat_id = get('item', 'category_id')
			item_type = get('item_type', 'code')
			required = get_required(get)

			try:
				props = categories[cat_id]['properties']
				props[name] = {'type': item_type, 'required': required}
			except KeyError:
				# I don't think that this should happen, but it does.  In
				# my estimation this is an error in the schema.
				_log.info('Found an item ({}) without a category.'.format(name))

	return categories


def get_required(getter):
	req = getter('item', 'mandatory_code')
	if req == None or req == 'no':
		return False
	else:
		return True


def get_item_name(getter):
	name = getter('item', 'name')
	return re.search('\w*\.(.*)', name).group(1)


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
