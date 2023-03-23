#!/usr/bin/env python3
# /* ex: set fenc=utf-8 expandtab ts=4 sw=4 : */
# Copyright: (c) 2019, Whitney Champion <whitney.ellis.champion@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
'''

EXAMPLES = '''
'''

RETURN = '''
'''


# import module snippets
import sys
#sys.path.insert(0, '/home/rumo/.virtualenvs/ansible/lib/python3.10/site-packages/')
#sys.path.insert(0, '/home/rumo/.virtualenvs/ansible/lib/python3.10/site-packages/ansible')
#sys.path.insert(0, '/home/rumo/.virtualenvs/ansible/lib/python3.10/site-packages/ansible/errors/')
#import ansible
#print('\n'.join(vars(ansible.module_utils.errors)))
#import ansible.errors
#from ansible.module_utils.errors import UnsupportedError
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.graylog import GraylogApi
from pprint import pprint

SUB_URI = 'system/lookup/tables'
LOOKUP_TABLES_URI = f'/api/{SUB_URI}'

def clean_table(stream):
    clean_data = {}
    remove_fields = ['id']
    for item in stream.keys():
        if item not in remove_fields:
            clean_data[item] = stream[item]
#   for item in stream['rules']:
#       rule = {}
#       for field in item.keys():
#           if field not in remove_fields:
#               rule[field] = item[field]
#       clean_data['rules'].append(rule)
    return clean_data

def cache_name_to_id(name, api):
    _bool, item = api.exists('system/lookup/caches', 'name', name, 'caches')
    if item is None:
        return None
    return item.get('id', None)

def data_adapter_name_to_id(name, api):
    _bool, item = api.exists('system/lookup/adapters', 'name', name, 'data_adapters')
    if item is None:
        return None
    return item.get('id', None)

def ensure(module, api):
    changed = False
    name = module.params['name']
    exists, table = api.exists(SUB_URI, 'name', name, list_result_keyA=['lookup_tables'])
    diff = None
    if module.params['state'] == 'present':
        cache_id = cache_name_to_id(module.params['cache'], api)
        if cache_id is None:
            raise BaseException("can't find cache with name {}".format(module.params['cache']))
        data_adapter_id = data_adapter_name_to_id(module.params['adapter'], api)
        if data_adapter_id is None:
            raise BaseException("can't find data adapter with name {}".format(module.params['adapter']))
        data = {
            'description':               module.params['description'],
            'title':                     module.params['title'] or name,
            'name':                      name,
            'content_pack':              module.params['content_pack'],
            'cache_id':                  cache_id,
            'data_adapter_id':           data_adapter_id,
            'default_multi_value':       module.params['default_multi_value'],
            'default_multi_value_type':  module.params['default_multi_value_type'],
            'default_single_value':      module.params['default_single_value'],
            'default_single_value_type': module.params['default_single_value_type'],
            }
        if exists:
#           pprint(adapter)
#           pprint(data)
            clean_table_data = clean_table(table)
            if clean_table_data != data:
                diff = dict(before=clean_table_data, after=data.copy(), action='updated')
                data['id'] = table['id']
                api.update(LOOKUP_TABLES_URI + '/' + table['id'], data)
                changed = True
            else:
                diff = dict(action='noop', submsg=f'existing table match specifications for name {name}')
        else:
            r = api.create(LOOKUP_TABLES_URI, data)
            diff = dict(action='created', after=r)
            changed = True
    else:
        if exists:
            api.delete(LOOKUP_TABLES_URI + '/' + table['id'])
            changed = True
            diff = dict(action='deleted', before=table)
        else:
            diff = dict(action='noop', submsg=f'no existing table with name {name}')
    return changed, diff



def main():
    module = AnsibleModule(
        argument_spec=dict(
            endpoint=dict(type='str'),
            graylog_user=dict(type='str'),
            graylog_password=dict(type='str', no_log=True),
            validate_certs=dict(type='bool', required=False, default=True),
            state=dict(type='str', required=False, default='present', choices=['present', 'absent']),
            title=dict(type='str', required=False, default=''),
            name=dict(type='str', required=True),
            description=dict(type='str', required=False, default=''),
            content_pack=dict(type='str'),
            cache=dict(type='str', required=True),
            adapter=dict(type='str', required=True),
            default_multi_value=dict(type='str', default='', required=False),
            default_multi_value_type=dict(type='str', default='NULL', required=False),
            default_single_value=dict(type='str', default='-', required=False),
            default_single_value_type=dict(type='str', default='NULL', required=False),
        ))

    api = GraylogApi(module.params['graylog_user'], module.params['graylog_password'], module.params['endpoint'], validate_certs=module.params['validate_certs'])
    api.login()
#   if module.params['matching_type']:
#       module.params['matching_type'] = module.params['matching_type'].upper()
    changed, diff = ensure(module, api)
#   try:
#   except BaseException as error:
#     module.fail_json(msg='unexpected error: ' + str(error))
    module.exit_json(changed=changed, msg=diff)


if __name__ == '__main__':
    main()
