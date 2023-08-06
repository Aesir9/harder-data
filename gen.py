import json
import os
import string

import yaml

ALLOWED_SLUG_CHARS = '-{}{}'.format(string.ascii_letters, string.digits)

out_json = {'red': 'red.json', 'blue': 'blue.json'}

required_fields = ['name', 'description', 'commands', 'tags']
command_fields = ['command', 'description']
tag_fields = ['name', 'slug']
optional_fields = ['references', 'links', 'show']
show_options = ['description', 'command']
autogen_fields = ['slug', 'id']
# Output Json needs to have these Keys:
# {
#   id: INT,
#   name: STRING
#   slug: STRING,
#   description: STRING,
#   references: [ LIST OF URLS ],
#   commands: [
#     { command: STRING, description: STRING }
#   ],
#   tags: [
#     { name: 'Execution', slug: 'execution' }
#   ]
#   links: [ LIST OF SLUGS ],
#   show: description | command
# }

# yapf: disable
BLUE_TAGS = [
    # what are you looking for?
    {'name': 'Execution',       'slug': 'execution'},
    {'name': 'Artifact',        'slug': 'artifact'},
    {'name': 'Download',        'slug': 'download'},
    {'name': 'Authentication',  'slug': 'authentication'},
    {'name': 'Command',         'slug': 'command'},
    {'name': 'Account',         'slug': 'account'},
    {'name': 'Persistence',     'slug': 'persistence'},

    # what do you have?
    {'name': 'Memory',          'slug': 'memory'},
    {'name': 'Event Log',       'slug': 'event-log'},
    {'name': 'Registry',        'slug': 'registry'},
    {'name': 'Network Caputre', 'slug': 'network-capture'},
    {'name': 'MS Office',       'slug': 'office'},
    {'name': 'Disk Image',      'slug': 'disk-image'},
]

RED_TAGS = [
    # Attack Types
    {'name': 'Enumeration',          'slug': 'enumeration'},
    {'name': 'Exploitation',         'slug': 'exploitation'},
    {'name': 'Privilege Escalation', 'slug': 'privilege-escalation'},
    {'name': 'Persistence',          'slug': 'persistence'},

    # Targets
    {'name': 'Web',        'slug': 'web'},
    {'name': 'SMB',        'slug': 'smb'},
    {'name': 'LDAP',       'slug': 'ldap'},
    {'name': 'PowerShell', 'slug': 'powershell'},
]
# yapf: enable


class Tool:
    def __init__(self, file_name, i, category):
        self.fpath = os.path.join(category, file_name)
        self.file_name = file_name
        self.slug = file_name.replace('.yaml', '').lower()
        self.id = i
        self.category = category

        self.has_error = False
        self.error_with = []

        data = None
        with open(self.fpath, 'r', encoding='UTF-8') as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                self.has_error = True
                self.error_with(f'YAML:: Failed parsing yaml data: {str(e)}')

        self.data = data

    def parse(self):
        # verify slug
        illegal = [c for c in self.slug if c not in ALLOWED_SLUG_CHARS]
        if len(illegal) > 0:
            self.has_error = True
            self.error_with.append(f'FILE :: Slug not valid, illegal chars: "{", ".join(illegal)}"')

        # add fields
        self.data['slug'] = self.slug
        self.data['id'] = self.id

        # verify format
        self.verify_fields()
        self.verify_tags()
        self.verify_commands()
        self.verify_show()

        # strip empty optional tags
        for opt in optional_fields:
            if opt in self.data:
                if isinstance(self.data[opt], list):
                    # check if the first entry is None
                    if len(self.data[opt]) > 0 and self.data[opt][0] is None:
                        self.data.pop(opt)

    def verify_fields(self):
        has_error = False
        # check if fields are missing
        for reqfield in required_fields:
            if reqfield not in self.data:
                has_error = True
                self.error_with.append(f'FILE :: Missing field: {reqfield}')

        # check typos
        level0_fields = self.data.keys()
        all_possible_fields = [*required_fields, *optional_fields, *autogen_fields]

        for field in level0_fields:
            if field not in all_possible_fields:
                has_error = True
                self.error_with.append(f'FILE :: Unrecognized field: {field}')

        if has_error:
            self.has_error = has_error

    def verify_tags(self):
        TAG_MAP = None
        if self.category == "red":
            TAG_MAP = RED_TAGS
        elif self.category == "blue":
            TAG_MAP = BLUE_TAGS

        has_error = False
        tags = set(self.data.pop('tags', []))
        self.data['tags'] = []
        for tag in tags:
            try:
                full_tag = next(t for t in TAG_MAP if t['slug'] == tag)
            except StopIteration:
                self.error_with.append(f'TAGS :: Invalid tag: {tag}')
                has_error = True
                continue
            self.data['tags'].append(full_tag)
        if has_error:
            self.has_error = has_error

    def verify_commands(self):
        has_error = False
        if 'commands' not in self.data:
            self.has_error = True
            return

        for cmd in self.data['commands']:
            for cmd_field in cmd.keys():
                if cmd_field not in command_fields:
                    self.error_with.append(f'COMMANDS :: Missing field: {cmd_field}')
                    has_error = True
        if has_error:
            self.has_error = has_error

    def verify_show(self):
        has_error = False
        if 'show' in self.data:
            if self.data['show'] is None:
                self.data.pop('show')
            else:
                if self.data['show'] not in show_options:
                    self.error_with.append('SHOW :: Invalid field: {}'.format(self.data['show']))
                    has_error = True
        if has_error:
            self.has_error = has_error


if __name__ == '__main__':
    total_tools = 0
    file_errors = 0

    for category in ['red', 'blue']:
        tools = []

        print(f'CATEGORY: {category}')
        files = os.listdir(category)
        for i, file in enumerate(files):
            if not file.endswith('.yaml'):
                continue

            tool = Tool(file, i, category)
            tool.parse()
            if tool.has_error:
                print(f'Errors with file: {tool.fpath}')
                for line in tool.error_with:
                    print(line)
                print('Supplied fields: ' + ', '.join(tool.data.keys()) + '\n')
                file_errors += 1
            else:
                print(f'Adding: {tool.slug}')
                tools.append(tool.data)

        with open(out_json[category], 'w', encoding='UTF-8') as out:
            json.dump(tools, out)

        total_tools += len(tools)

    print(f'TOOLS: {total_tools} :: ERRORS: {file_errors}')
