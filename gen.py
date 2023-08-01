import os
import yaml
import json

out_json = 'data.json'

required_fields = ['name', 'description', 'commands', 'tags']
command_fields = ['command', 'description']
tag_fields = ['name', 'slug']
optional_fields = ['references', 'links']

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
#   links: [ LIST OF SLUGS ]
# }

# yapf: disable
TAGS = [
    # what are you looking for?
    {'name': 'Execution',       'slug': 'execution'},
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
# yapf: enable


class Tool:
    def __init__(self, file_name, i):
        self.fpath = os.path.join('data', file_name)
        self.file_name = file_name
        self.slug = file_name.replace('.yaml', '')
        self.id = i

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
        # add fields
        self.data['slug'] = self.slug
        self.data['id'] = self.id

        # verify format
        self.verify_fields()
        self.verify_tags()
        self.verify_commands()

    def verify_fields(self):
        has_error = False
        for reqfield in required_fields:
            if reqfield not in self.data:
                has_error = True
                self.error_with.append(f'FILE :: Missing field: {reqfield}')

        if has_error:
            self.has_error = has_error

    def verify_tags(self):
        has_error = False
        tags = self.data.pop('tags', [])
        self.data['tags'] = []
        for tag in tags:
            try:
                full_tag = next(t for t in TAGS if t['slug'] == tag)
            except StopIteration:
                self.error_with.append(f'TAGS :: Invalid tag: {tag}')
                has_error = True
                continue
            self.data['tags'].append(full_tag)
        if has_error:
            self.has_eror = has_error

    def verify_commands(self):
        has_error = False
        if 'commands' not in self.data:
            self.has_eror = True
            return

        for cmd in self.data['commands']:
            for cmd_field in cmd.keys():
                if cmd_field not in command_fields:
                    self.error_with.append(f'COMMANDS :: Missing field: {cmd_field}')
                    has_error = True
        if has_error:
            self.has_error = has_error


if __name__ == '__main__':
    files = os.listdir('data/')
    tools = []
    file_errors = 0

    for i, file in enumerate(files):
        if not file.endswith('.yaml'):
            continue

        tool = Tool(file, i)
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

    print(f'TOOLS: {len(tools)} :: ERRORS: {file_errors}')
    with open(out_json, 'w', encoding='UTF-8') as out:
        json.dump(tools, out)
