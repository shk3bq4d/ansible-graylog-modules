#!/usr/bin/python
# Copyright: (c) 2019, Whitney Champion <whitney.ellis.champion@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
module: graylog_roles
short_description: Communicate with the Graylog API to manage roles
description:
    - The Graylog roles module manages Graylog roles.
version_added: "2.9"
author: "Whitney Champion (@shortstack)"
options:
  endpoint:
    description:
      - Graylog endoint. (i.e. graylog.mydomain.com).
    required: false
    type: str
  graylog_user:
    description:
      - Graylog privileged user username.
    required: false
    type: str
  graylog_password:
    description:
      - Graylog privileged user password.
    required: false
    type: str
  validate_certs:
    description:
      - Allow untrusted certificate
    required: false
    default: false
    type: bool          
  state:
    description:
      - Action to take with the defined role.
    required: false
    default: present
    choices: [ present, absent ]
    type: str
  name:
    description:
      - Role name.
    required: false
    type: str
  description:
    description:
      - Role description.
    required: false
    type: str
  permissions:
    description:
      - Permissions list for role.
    required: false
    type: list
  read_only:
    description:
      - Read only, true or false.
    required: false
    default: "false"
    type: str
'''

EXAMPLES = '''

# Create role
- graylog_roles:
    state: present
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"
    name: "analysts"
    description: "Analyst role"
    permissions:
      - "streams:read"
      - "dashboards:read"
    read_only: "true"

# Create admin role
- graylog_roles:
    state: present
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"
    name: "admins"
    description: "Admin role"
    permissions:
      - "*"
    read_only: "false"

# Delete role
- graylog_roles:
    state: absent
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"
    name: "admins"
'''

RETURN = '''
json:
  description: The JSON response from the Graylog API
  returned: always
  type: complex
  contains:
      name:
          description: Role name.
          returned: success
          type: str
          sample: 'Administrators'
      description:
          description: Role description.
          returned: success
          type: str
          sample: 'Administrators group'
      permissions:
          description: Role permissions (dashboards, streams, collectors, etc).
          returned: success
          type: list
          sample: [ "dashboards:read:4c58eef77ec84145c3a2d9f3", "sidecars:update" ]
      read_only:
          description: Whether or not the role is a read-only role.
          returned: success
          type: bool
          sample: false
status:
  description: The HTTP status code from the request
  returned: always
  type: int
  sample: 200
url:
  description: The actual URL used for the request
  returned: always
  type: str
  sample: https://www.ansible.com/
'''


# import module snippets
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.graylog import GraylogApi

ROLES_URI = '/api/roles/'


def ensure(module, api):
  changed = False
  exists, role = api.exists('roles', 'name', module.params['name'])
  #user sorted to ensure data is in the same order
  if module.params['state'] == 'present':
    data = {'description': module.params['description'], 'name': module.params['name'], 'permissions': sorted(module.params['permissions']), 'read_only': module.params['read_only']}
    if exists:
      role['permissions'] = sorted(role['permissions'])
      if role != data:
        api.update(ROLES_URI + module.params['name'], data)
        changed = True
    else:
      api.create(ROLES_URI, data)
      changed = True
  else:
    if exists:
      api.delete(ROLES_URI + module.params['name'])
      changed = True
  return changed


def main():
    module = AnsibleModule(
        argument_spec=dict(
            endpoint=dict(type='str'),
            graylog_user=dict(type='str'),
            graylog_password=dict(type='str', no_log=True),
            validate_certs=dict(type='bool', required=False, default=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            name=dict(type='str', required=True),
            description=dict(type='str'),
            permissions=dict(type='list'),
            read_only=dict(type='bool', default=False)
        )
    )
    try:
      api = GraylogApi(module.params['graylog_user'], module.params['graylog_password'], module.params['endpoint'], validate_certs=module.params['validate_certs'])
      api.login()
      changed = ensure(module, api)
    except Exception as error:
      module.fail_json(msg='unexpected error: ' + str(error))
    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
