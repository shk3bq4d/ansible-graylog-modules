#!/usr/bin/python
# Copyright: (c) 2020, Philip Bove <phil@bove.online>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
module: graylog_roles_info
short_description: List graylog roles
description:
  - List graylog roles
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
'''


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.graylog import GraylogApi

ROLES_URI = '/api/roles'


def main():
    module = AnsibleModule(
        argument_spec=dict(
            endpoint=dict(type='str', required=True),
            graylog_user=dict(type='str'),
            graylog_password=dict(type='str', no_log=True),
            validate_certs=dict(type='bool', required=False, default=True)
        )
    )
    try:
        api = GraylogApi(module.params['graylog_user'], module.params['graylog_password'], module.params['endpoint'], validate_certs=module.params['validate_certs'])
        api.login()
        roles = api.get(ROLES_URI)['roles']
    except Exception as error:
      module.fail_json(msg='unexpected error: ' + str(error))
    module.exit_json(changed=False, roles=roles)


if __name__ == '__main__':
    main()