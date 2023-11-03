from datetime import datetime
import json
import os
import re
import requests
import dotenv
dotenv.load_dotenv()

input_json = 'atlas_converted.json'
output_json = 'atlas_notion.json'


# Initialize the Notion API token and endpoint
NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
NOTION_API_BASE_URL = os.getenv('NOTION_API_BASE_URL')

if NOTION_API_BASE_URL is None:
    raise Exception('NOTION_API_TOKEN has not been defined in .env')
if NOTION_API_TOKEN is None:
    raise Exception('NOTION_API_TOKEN has not been defined in .env')

# Set up headers
headers = {
    'Authorization': f'Bearer {NOTION_API_TOKEN}',
    'Notion-Version': '2022-06-28'
}

def get_database_meta(database_id):
    response = requests.get(f'{NOTION_API_BASE_URL}/databases/{database_id}', headers=headers)
    return response.json()

def get_database_rows(database_id):
    response = requests.post(f'{NOTION_API_BASE_URL}/databases/{database_id}/query', {}, headers=headers)
    return response.json()

def get_rows(database_id):
    response = get_database_rows(database_id)
    lst = []
    for row in response['results']:
        if (not any (row['properties']['ID']['title'])):
            continue
        d = {}
        for column_name, column_value in row['properties'].items():
            if column_value.get('title'):
                d[column_name] = column_value['title'][0]['text']['content'] if any(column_value['title']) else None
            elif column_value.get('multi_select'):
                d[column_name] = column_value['multi_select'][0]['name'] if any(column_value['multi_select']) else None
            elif column_value.get('rich_text'):
                d[column_name] = column_value['rich_text'][0]['text']['content'] if any(column_value['rich_text']) else None
            elif column_value.get('select'):
                d[column_name] = column_value['select']['name'] if column_value['select'] else None
            elif column_value.get('status'):
                d[column_name] = column_value['status']['name'] if column_value['status'] else None
            # Add more conditions for other types if needed
            else:
                d[column_name] = None
        lst.append(d)
        list.reverse(lst) # notion documents are read from bottom up
    return lst

def alphanumeric_key(key):
    return [int(c) if c.isdigit() else c for c in re.split('([0-9]+)', key)]

def sort_dictionary(d):
    return dict(sorted(d.items(), key=lambda x: alphanumeric_key(x[0])))

def make_dict(notion_rows: list[dict]):
    d = {}
    for row in notion_rows:
        article_no = row['Article No.']
        d.setdefault(article_no, []).append(row)
        sorted(d.items(), key=lambda x: x[0])
    return sort_dictionary(d)

def merge_into_atlas(atlas: dict, d: dict[str, list[dict]], suffix):
    for k,v in d.items():
        supporting_root_key = f'{k}.0'
        if supporting_root_key not in atlas:
            atlas[supporting_root_key] = {
                'Name': 'Supporting Root',
                'Version': 1,
                'Type': 'Supporting Root',
                'Last_Modified': datetime.now().strftime('%Y-%m-%d'),
                'Child_Documents': [],
                'links_to': {},
                'linked_from': []
            }
        identifier = f'{supporting_root_key}.{suffix}'
        dict_exists = atlas.get(identifier) is not None
        if not dict_exists:
            if suffix == 2:
                atlas[identifier] = {
                    'Name': 'Element Analysis Directory',
                    'Version': 1,
                    'Type': 'Element Analysis Directory',
                    'Components': {
                        'List of Elements and their Element Analysis Documents': {}
                    },
                    'Last_Modified': datetime.now().strftime('%Y-%m-%d'),
                    'Child_Documents': [],
                    'links_to': {},
                    'linked_from': []
                }
            if suffix == 3:
                atlas[identifier] = {
                    'Name': 'FacilitatorDAO Action Example Directory',
                    'Version': 1,
                    'Type': 'FacilitatorDAO Action Example Directory',
                    'Components': {
                        'Directory overview': 'This directory contains examples of hypothetical FacilitatorDAO actions in response to AVC governance issues, to serve as a guide for future decision-making.'
                    },
                    'Last_Modified': datetime.now().strftime('%Y-%m-%d'),
                    'Child_Documents': [],
                    'links_to': {},
                    'linked_from': []
                }
            atlas[supporting_root_key]["Child_Documents"].append(identifier)
        keys = list(atlas.keys())
        matched_keys = [int(k[len(identifier)+1:]) for k in keys if k.startswith(f'{identifier}.')]
        
        highest_key = None if not any(matched_keys) else max(matched_keys)
        key = 1 if highest_key is None else highest_key + 1
        child_documents = []
        analysis_child_documents = {}
        for row in v:
            # check if an item with that name already exists, override content if so
            flag = False
            for k in matched_keys:
                if atlas[f'{identifier}.{k}']['Name'] == row['Name']:
                    flag = True
                    if suffix == 2:
                        atlas[f'{identifier}.{k}']['Components'] = {
                            'Element': row['Relevant word or sentence'],
                            'Analysis': row['Analysis or Definition']
                        }
                    if suffix == 3:
                        atlas[f'{identifier}.{k}']['Components'] = {
                        'Input': row['Input'],
                        'Output': row['Output'],
                        'Label': row['Label']
                        }
                        
                        if row['Label'] == 'Misaligned':
                            atlas[f'{identifier}.{k}']['Components']['Penalty'] = row['Penalty']
                            atlas[f'{identifier}.{k}']['Components']['Penalty_Reason'] = row['Penalty_Reason']
                    

                    atlas[f'{identifier}.{k}']['Last_Modified']: datetime.now().strftime('%Y-%m-%d')
                    break
            if flag:
                continue
            
            
            child_documents.append(f'{identifier}.{key}')
            
            # row was an element analysis
            if suffix == 2:
                analysis_child_documents[row['Name']] = f'{identifier}.{key}'
                atlas[f'{identifier}.{key}'] = {
                    'Name': row['Name'],
                    'Version': 1,
                    'Type': row['Task'],
                    'Components': {
                        'Element': row['Relevant word or sentence'],
                        'Analysis': row['Analysis or Definition']
                    },
                    'Last_Modified': datetime.now().strftime('%Y-%m-%d'),
                    'Child_Documents': [],
                    'links_to': {},
                    'linked_from': []
                }
            # row was a facilitatordao action
            if suffix == 3:
                atlas[f'{identifier}.{key}'] = {
                    'Name': row['Name'],
                    'Version': 1,
                    'Type': row['Task'],
                    'Components': {
                        'Input': row['Input'],
                        'Output': row['Output'],
                        'Label': row['Label'],
                    },
                    'Last_Modified': datetime.now().strftime('%Y-%m-%d'),
                    'Child_Documents': [],
                    'links_to': {},
                    'linked_from': []
                }
                if row['Label'] == 'Misaligned':
                    atlas[f'{identifier}.{key}']['Components']['Penalty'] = row['Penalty']
                    atlas[f'{identifier}.{key}']['Components']['Penalty_Reason'] = row['Penalty_Reason']
            key += 1
        
        if suffix == 2:
            for k,v in analysis_child_documents.items():
                atlas[identifier]['Components']['List of Elements and their Element Analysis Documents'][k] = v
        for d in child_documents:
            atlas[identifier]['Child_Documents'].append(d)
    return atlas


# read notion pages into a dict on type {"A.1.5.1": [{}, {}]}
element_analysis_rows = get_rows('a8c9df7e3cc24211aab88eb7973cfcda')
facilitator_rows = get_rows('b9aebea4c9a04bcdaabb7987e6954509')
element_dict = make_dict(element_analysis_rows)
facilitator_dict = make_dict(facilitator_rows)


# load atlas
atlas = {}
with open(output_json, 'w') as file:
    json.dump(atlas, file, indent=4)

atlas = merge_into_atlas(atlas, element_dict, 2)
atlas = merge_into_atlas(atlas, facilitator_dict, 3)
atlas = sort_dictionary(atlas)

# write atlas
with open(output_json, 'w') as file:
    json.dump(atlas, file)
