import os
import yaml
import json

out_json = 'data.json'

required_fields = ['name', 'description', 'commands', 'tags']
command_fields = ['command', 'description']
tag_fields = ['name', 'slug']
optional_fields = ['references']

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
# }

# yapf: disable
TAGS = [
    {'name': 'Execution',      'slug': 'execution'},
    {'name': 'Event Log',      'slug': 'event-log'},
    {'name': 'Persistence',    'slug': 'persistence'},
    {'name': 'Authentication', 'slug': 'authentication'},
    {'name': 'Command',        'slug': 'command'},
    {'name': 'Account',        'slug': 'account'},
    {'name': 'Persistence',    'slug': 'persistence'},
    {'name': 'Registry',       'slug': 'registry'},
    {'name': 'Disk Image',     'slug': 'disk-image'},
    {'name': 'MS Office',      'slug': 'office'},
]
# yapf: enable

if __name__ == '__main__':
    files = os.listdir('data/')
    tools = []
    for i, file in enumerate(files):
        if not file.endswith('.yaml'):
            continue

        file_path = os.path.join('data', file)
        with open(file_path, 'r', encoding='UTF-8') as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(e)
        print(data)
        # Check required_fields
        found_missing = False
        for reqfield in required_fields:
            if reqfield not in data:
                found_missing = True
                print(f'ERROR MISSING: {reqfield}')

        if found_missing:
            print(f'Ignoring: {file}')
            continue

        # gen required fields
        data['slug'] = file.replace('.yaml', '')
        data['id'] = i

        # check tags
        found_invalid_tag = False
        tags = data.pop('tags')
        data['tags'] = []
        for tag in tags:
            try:
                full_tag = next(t for t in TAGS if t['slug'] == tag)
            except StopIteration:
                print(f'INVALID TAG: {tag}')
                found_invalid_tag = True
                continue
            data['tags'].append(full_tag)

        tools.append(data)

    with open(out_json, 'w', encoding='UTF-8') as out:
        json.dump(tools, out)
