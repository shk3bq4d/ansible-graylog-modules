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

SUB_URI = 'system/lookup/caches'
LOOKUP_CACHES_URI = f'/api/{SUB_URI}'

def clean_cache(stream):
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
    exists, cache = api.exists(SUB_URI, 'name', name)
    diff = None
    if module.params['state'] == 'present':
        data = {
            'description': module.params['description'],
            'title':       module.params['title'] or name,
            'name':       name, 
            'content_pack':       module.params['content_pack'], 
            'config': dict(
                type='guava_cache',
                expire_after_write_unit=None,
                expire_after_access=module.params['config']['expire_after_access'],
                expire_after_access_unit=module.params['config']['expire_after_access_unit'],
                expire_after_write=module.params['config']['expire_after_write'],
                max_size=module.params['config']['max_size'],
                ),
            }
        if exists:
#           pprint(cache)
#           pprint(data)
            clean_cache_data = clean_cache(cache)
            if clean_cache_data != data:
                diff = dict(before=clean_cache_data, after=data.copy(), action='updated')
                data['id'] = cache['id']
                api.update(LOOKUP_CACHES_URI + '/' + cache['id'], data)
                changed = True
            else:
                diff = dict(action='noop', submsg=f'existing cache match specifications for name {name}')
        else:
            r = api.create(LOOKUP_CACHES_URI, data)
            diff = dict(action='created', after=r)
            changed = True
    else:
        if exists:
            api.delete(LOOKUP_CACHES_URI + '/' + cache['id'])
            changed = True
            diff = dict(action='deleted', before=cache)
        else:
            diff = dict(action='noop', submsg=f'no existing cache with name {name}')
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
            id=dict(type='str'),
            config=dict(
                type="dict",
                required=False,
                options=dict(
                    expire_after_access=dict(type='int', default=12, required=False),
                    expire_after_access_unit=dict(type='str', default='HOURS', required=False, choices=['HOURS','SECONDS']),
                    expire_after_write=dict(type='int', default=0, required=False),
                    max_size=dict(type='int', default=0, required=False),
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
