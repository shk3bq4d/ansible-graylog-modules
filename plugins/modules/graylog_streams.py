#!/usr/bin/python
# Copyright: (c) 2019, Whitney Champion <whitney.ellis.champion@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
module: graylog_streams
short_description: Communicate with the Graylog API to manage streams
description:
    - The Graylog streams module manages Graylog streams.
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
  allow_http:
    description:
      - Allow non HTTPS connexion
    required: false
    default: false
    type: bool    
  validate_certs:
    description:
      - Allow untrusted certificate
    required: false
    default: false
    type: bool      
  action:
    description:
      - Action to take against stream API.
    required: false
    default: list
    choices: [ create, create_rule, start, pause, update, update_rule, delete, delete_rule, list, query_streams ]
    type: str
  title:
    description:
      - Stream title.
    required: false
    type: str
  description:
    description:
      - Stream description.
    required: false
    type: str
  stream_id:
    description:
      - Stream ID.
    required: false
    type: str
  rule_id:
    description:
      - Rule ID.
    required: false
    type: str
  index_set_id:
    description:
      - Index set ID.
    required: false
    type: str
  matching_type:
    description:
      - Matching type for the stream rules.
    required: false
    type: str
  remove_matches_from_default_stream:
    description:
      - Remove matches from default stream, true or false.
    required: false
    default: False
    type: bool
  stream_name:
    description:
      - Stream name to use with the query_streams action.
    required: false
    type: str
  field:
    description:
      - Field name for the stream rule to check.
    required: false
    type: str
  type:
    description:
      - Rule type for the stream rule, 1-7.
    required: false
    default: 1
    type: int
  value:
    description:
      - Value to check rule against.
    required: false
    type: str
  inverted:
    description:
      - Invert rule (must not match value).
    required: false
    default: False
    type: bool
  rules:
    description:
      - List of rules associated with a stream.
    required: false
    type: list
'''

EXAMPLES = '''
# List streams
- graylog_streams:
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"

# Get stream from stream name query_streams
- graylog_streams:
    action: query_streams
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"
    stream_name: "test_stream"
  register: stream

# List single stream by ID
- graylog_streams:
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"
    stream_id: "{{ stream.json.id }}"

# Create stream
- graylog_streams:
    action: create
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"
    title: "Client XYZ"
    description: "Windows and IIS logs"
    matching_type: "AND"
    remove_matches_from_default_stream: False
    rules:
      - '{"field":"message", "type":"6", "value":"test", "inverted":true, "description":"testrule"}'

# Update stream
- graylog_streams:
    action: update
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"
    stream_id: "{{ stream.json.id }}"
    remove_matches_from_default_stream: True

# Create stream rule
- graylog_streams:
    action: create_rule
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"
    stream_id: "{{ stream.json.id }}"
    description: "Windows Security Logs"
    field: "winlogbeat_log_name"
    type: 1
    value: "Security"
    inverted: False

# Start stream
- graylog_streams:
    action: start
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"
    stream_id: "{{ stream.json.id }}"

# Pause stream
- graylog_streams:
    action: pause
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"
    stream_id: "{{ stream.json.id }}"

# Update stream rule
- graylog_streams:
    action: update_rule
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"
    stream_id: "{{ stream.json.id }}"
    rule_id: "{{ rule.json.id }}"
    description: "Windows Security and Application Logs"

# Delete stream rule
- graylog_streams:
    action: delete_rule
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"
    stream_id: "{{ stream.json.id }}"
    rule_id: "{{ rule.json.id }}"

# Delete stream
- graylog_streams:
    action: delete
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"
    stream_id: "{{ stream.json.id }}"
'''

RETURN = '''
json:
  description: The JSON response from the Graylog API
  returned: always
  type: complex
  contains:
    title:
      description: Stream title.
      returned: success
      type: str
      sample: 'Windows Logs'
    alert_conditions:
      description: Alert conditions.
      returned: success
      type: dict
      sample: |
        [
            {
                "created_at": "2018-10-18T18:40:21.582+0000",
                "creator_user_id": "admin",
                "id": "cc43d4e7-e7b2-4abc-7c44-4b29cadaf364",
                "parameters": {
                    "backlog": 1,
                    "grace": 0,
                    "repeat_notifications": true,
                    "threshold": 0,
                    "threshold_type": "MORE",
                    "time": 1
                },
                "title": "Failed Logon",
                "type": "message_count"
            }
        ]
    alert_receivers:
        description: Alert receivers.
        returned: success
        type: dict
        sample: '{ "emails": [], "users": [] }'
    content_pack:
        description: Content pack.
        returned: success
        type: str
        sample: null
    created_at:
        description: Stream creation time.
        returned: success
        type: str
        sample: "2018-10-17T15:29:20.735Z"
    creator_user_id:
        description: Stream creator.
        returned: success
        type: str
        sample: "admin"
    description:
        description: Stream description.
        returned: success
        type: str
        sample: "Stream for Windows logs"
    disabled:
        description: Whether or not the stream is enabled.
        returned: success
        type: bool
        sample: false
    id:
        description: Stream ID.
        returned: success
        type: str
        sample: "5bc7666089675c7f7d7f08d7"
    index_set_id:
        description: Index set ID associated with the stream.
        returned: success
        type: str
        sample: "4bc7444089575c7f7d7f08d7"
    is_default:
        description: Whether or not it is the default stream.
        returned: success
        type: bool
        sample: false
    matching_type:
        description: Stream rule matching type.
        returned: success
        type: str
        sample: "AND"
    outputs:
        description: Stream outputs.
        returned: success
        type: dict
        sample: []
    remove_matches_from_default_stream:
        description: Whether or messages are removed from the default stream.
        returned: success
        type: bool
        sample: false
    rules:
        description: Rules associated with the stream.
        returned: success
        type: dict
        sample: []
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
from ansible.errors import AnsibleError

STREAMS_URI = '/api/streams/'


def clean_stream(stream):
    clean_data = {}
    remove_fields = ['id', 'stream_id', 'created_at', 'alert_receivers', 'alert_conditions', 'content_pack', 'outputs', 'creator_user_id', 'is_default']
    for item in stream.keys():
        if item not in remove_fields:
            clean_data[item] = stream[item]
    for item in stream['rules']:
        rule = {}
        for field in item.keys():
            if field not in remove_fields:
                rule[field] = item[field]
        clean_data['rules'].append(rule)
    return clean_data


def generate_rule_id_map(current_rules):
    rules_map = {}
    for item in current_rules:
        item['description'] = item['id']
    return rules_map


def prep_rules(rules, id_map):
    for rule in rules:
        if rule['description'] in id_map.keys():
            rule['id'] = id_map['description']
    return rules


def index_set_name_to_id(name, api):
    resp = api.get('/api/system/indices/index_sets')
    for item in resp['index_sets']:
        if item['title'] == name:
            return item['id']
    return None


def ensure(module, api):
    changed = False
    exists, stream = api.exists('streams', 'title', module.params['title'])
    index_set_id = index_set_name_to_id(module.params['index_set'], api)
    if not index_set_id:
        module.fail_json(msg='index set provided does not exist!')
    if module.params['state'] == 'present':
        data = {'description': module.params['description'], 'title': module.params['title'], 'rules': module.params['rules'], 
        'remove_matches_from_default_stream': module.params['remove_matches_from_default_stream'], 'matching_type': module.params['matching_type'], 
        'index_set_id': index_set_id, 'disabled': module.params['disabled']}
        if exists:
            clean_stream_data = clean_stream(stream)
            rule_id_map = generate_rule_id_map(stream['roles'])
            if clean_data != data:
                data['rules'] = prep_rules(data['rules'], rule_id_map)
                api.update(STREAMS_URI + stream['id'], data)
                changed = True
        else:
            api.create(STREAMS_URI, data)
            changed = True
    else:
        if exists:
          api.delete(ROLES_URI + stream['id'])
          changed = True
    return changed



def main():
    module = AnsibleModule(
        argument_spec=dict(
            endpoint=dict(type='str'),
            graylog_user=dict(type='str'),
            graylog_password=dict(type='str', no_log=True),
            validate_certs=dict(type='bool', required=False, default=True),
            state=dict(type='str', required=False, default='present', choices=['present', 'absent']),
            title=dict(type='str'),
            description=dict(type='str'),
            disabled=dict(type='bool', default=False),
            index_set=dict(type='str', default='Default index set'),
            remove_matches_from_default_stream=dict(type='bool', default=False),
            matching_type=dict(type='str'),
            rules=dict(type='list')
        )
    )

    try:
      api = GraylogApi(module.params['graylog_user'], module.params['graylog_password'], module.params['endpoint'], validate_certs=module.params['validate_certs'])
      api.login()
      if module.params['matching_type']:
        module.params['matching_type'] = module.params['matching_type'].upper()
      changed = ensure(module, api)
    except AnsibleError as error:
      module.fail_json(msg='unexpected error: ' + str(error))
    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
