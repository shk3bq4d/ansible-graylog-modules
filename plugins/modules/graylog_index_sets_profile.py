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
import os
#sys.path.insert(0, os.path.expanduser('~/.virtualenvs/ansible/lib/python3.11/site-packages/'))
#sys.path.insert(0, os.path.expanduser('~/.virtualenvs/ansible/lib/python3.11/site-packages/ansible'))
#sys.path.insert(0, os.path.expanduser('~/.virtualenvs/ansible/lib/python3.11/site-packages/ansible/errors/'))
#import ansible
#print('\n'.join(vars(ansible.module_utils.errors)))
#import ansible.errors
#from ansible.module_utils.errors import UnsupportedError
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.graylog import GraylogApi
from pprint import pprint

SUB_URI = 'system/indices/index_sets/profiles'
INDEX_SETS_PROFILE_URI = f'/api/{SUB_URI}'

def clean_index_sets_profile(profile):
    clean_data = {}
    remove_fields = ['id', 'index_set_ids']
    for item in profile.keys():
        if item not in remove_fields:
            clean_data[item] = profile[item]
#   if 'index_set_ids' in profile:
#       profile['index_set_ids'].sort()
    if 'custom_field_mappings' in profile:
        profile['custom_field_mappings'].sort(key=lambda x: x['field'])
    return clean_data

def index_set_titles_to_ids(module, titles, api):
    rA = []
    index_sets = api.get('/api/system/indices/index_sets')['index_sets']
    for title in titles:
        found = False
        for index_set in index_sets:
            if index_set['title'] == title:
                found = True
                rA.append(index_set['id'])
                break
        if not found:
            module.fail_json(msg='could not find index_set with title: ' + title)
    return list(sorted(rA))

def custom_field_mappings_dict_to_list(foH):
    rA = []
    for field, type in foH.items():
        rA.append(dict(field=field, type=type))
    rA.sort(key=lambda x: x['field'])
    return rA

def ensure(module, api):
    changed = False
    name = module.params['name']
    exists = False
    #pprint(INDEX_SETS_PROFILE_URI + '/all')
    rA = api.get(INDEX_SETS_PROFILE_URI + '/all')
    #pprint(rA)
    for uH in rA:
        if uH['name'] == name:
            exists = True
            index_sets_profile = api.get(INDEX_SETS_PROFILE_URI + '/' + uH['id'])
            break

    diff = None
    if module.params['state'] == 'present':
        #index_set_ids = index_set_titles_to_ids(module, module.params['index_set_titles'], api)
        data = {
            'description': module.params.get('description', None),
            'name':       name,
#           'index_set_ids': index_set_ids,
            'custom_field_mappings': custom_field_mappings_dict_to_list(module.params['custom_field_mappings']),
            }
        if exists:
#           pprint(index_sets_profile)
#           pprint(data)
            clean_index_sets_profile_data = clean_index_sets_profile(index_sets_profile)
            if clean_index_sets_profile_data != data:
                diff = dict(before=clean_index_sets_profile_data, after=data.copy(), action='updated')
                data['id'] = index_sets_profile['id']
                api.update(INDEX_SETS_PROFILE_URI, data)
                changed = True
            else:
                diff = dict(action='noop', submsg=f'existing index_sets_profile match specifications for name {name}')
        else:
#           data.pop('index_set_ids')
            r = api.create(INDEX_SETS_PROFILE_URI, data)
            diff = dict(action='created', after=r)
            changed = True
#           for index_set_id in index_set_ids:
#               api.update('/api/system/indices/index_sets/' + index_set_id, dict(field_type_profile=r['id']))
    else:
        if exists:
            api.delete(INDEX_SETS_PROFILE_URI + '/' + index_sets_profile['id'])
            changed = True
            diff = dict(action='deleted', before=index_sets_profile)
        else:
            diff = dict(action='noop', submsg=f'no existing index_sets_profile with name {name}')
    return changed, diff



def main():
    module = AnsibleModule(
        argument_spec=dict(
            endpoint=dict(type='str'),
            graylog_user=dict(type='str'),
            graylog_password=dict(type='str', no_log=True),
            validate_certs=dict(type='bool', required=False, default=True),
            state=dict(type='str', required=False, default='present', choices=['present', 'absent']),
            name=dict(type='str', required=True),
            description=dict(type='str', required=False, default=''),
            id=dict(type='str'),
#           index_set_titles=dict(type="list", required=True, options=dict( type="str")),
            custom_field_mappings=dict(type="dict", required=True),
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
