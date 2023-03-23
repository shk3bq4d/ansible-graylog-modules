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

SUB_URI = 'system/lookup/adapters'
LOOKUP_ADAPTERS_URI = f'/api/{SUB_URI}'

def clean_adapter(stream):
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

def ensure(module, api):
    changed = False
    name = module.params['name']
    exists, adapter = api.exists(SUB_URI, 'name', name, list_result_keyA=['data_adapters'])
    diff = None
    if module.params['state'] == 'present':
        data = {
            'description': module.params['description'],
            'title':       module.params['title'] or name,
            'name':       name,
            'content_pack':       module.params['content_pack'],
            'custom_error_ttl': module.params['custom_error_ttl'],
            'custom_error_ttl_enabled': module.params['custom_error_ttl_enabled'],
            'custom_error_ttl_unit': module.params['custom_error_ttl_unit'],
            'config': {
                'case_insensitive_lookup': module.params['config']['case_insensitive_lookup'],
                'check_interval': module.params['config']['check_interval'],
                'key_column': module.params['config']['key_column'],
                'path': module.params['config']['path'],
                'quotechar': module.params['config']['quotechar'],
                'separator': module.params['config']['separator'],
                'type': module.params['config']['type'],
                'value_column': module.params['config']['value_column'],
                },
            }
        if exists:
#           pprint(adapter)
#           pprint(data)
            clean_adapter_data = clean_adapter(adapter)
            if clean_adapter_data != data:
                diff = dict(before=clean_adapter_data, after=data.copy(), action='updated')
                data['id'] = adapter['id']
                api.update(LOOKUP_ADAPTERS_URI + '/' + adapter['id'], data)
                changed = True
            else:
                diff = dict(action='noop', submsg=f'existing adapter match specifications for name {name}')
        else:
            r = api.create(LOOKUP_ADAPTERS_URI, data)
            diff = dict(action='created', after=r)
            changed = True
    else:
        if exists:
            api.delete(LOOKUP_ADAPTERS_URI + '/' + adapter['id'])
            changed = True
            diff = dict(action='deleted', before=adapter)
        else:
            diff = dict(action='noop', submsg=f'no existing adapter with name {name}')
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
            custom_error_ttl=dict(type='int', required=False, default=None),
            custom_error_ttl_enabled=dict(type='bool', required=False, default=False),
            custom_error_ttl_unit=dict(type='str', required=False, default=None),
            id=dict(type='str'),
            config=dict(
                type="dict",
                required=False,
                options=dict(
                    case_insensitive_lookup=dict(type='bool', default=False, required=False),
                    check_interval=dict(type='int', default=1800, required=False),
                    key_column=dict(type='str', required=True),
                    path=dict(type='str', required=True),
                    quotechar=dict(type='str', required=False, default='"'),
                    separator=dict(type='str', required=False, default=','),
                    type=dict(type='str', default='csvfile', required=False, choices=['csvfile']),
                    value_column=dict(type='str', required=True),
                    ),
                )
        )
    )

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
