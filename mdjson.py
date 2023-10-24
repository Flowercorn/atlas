import re
import json

def convert_md_to_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    output_json = {}
    main_counter = 0
    current_text = ""

    # Skip preamble
    lines = lines[lines.index("## 2: The Governance Scope - GOV\n"):]

    for line in lines:
        line = line.strip()
        match = re.match(r'^(#+) (.+)$', line)
        if line == "":
            continue
        if match:
            depth = len(match.group(1))
            name_parts = match.group(2).split(": ")
            name = name_parts[1] if len(name_parts) > 1 else ""
            if depth > 4:
                split_result = match.group(2).split(':')
                subtitle = ':'.join(split_result[1:])
                if subtitle.strip() != "":
                    if output_json[identifier]["Components"]["Content"]:
                        output_json[identifier]["Components"]["Content"] += f'\n{subtitle}, '
                    else:
                        output_json[identifier]["Components"]["Content"] += f'{subtitle}, '
                else:
                    output_json[identifier]["Components"]["Content"] += "\n"
                continue

            if depth == 2:
                main_counter += 1
            identifier_numbers = name_parts[0].split(".")[0:]
            if len(identifier_numbers) > 1:
                identifier = f"A.{main_counter}." + ".".join(identifier_numbers[1:])
            else:
                identifier = f"A.{main_counter}"
                
            output_json[identifier] = {
                "Name": name,
                "Version": 1,
                "Type": None,
                "Components": {
                    "Content": current_text.strip()
                },
                "Last_Modified": "2023-10-23-19:07:00",
                "Child_Documents": [],
                "links_to": {},
                "linked_from": []
            }
            current_text = ""
        else:
            output_json[identifier]["Components"]["Content"] += line

    # Add the last section
    if main_counter:
        last_identifier = list(output_json.keys())[-1]
        if output_json[last_identifier]["Components"]["Content"]:
            output_json[last_identifier]["Components"]["Content"] += '\n'
        output_json[last_identifier]["Components"]["Content"] += current_text.strip()

    return output_json

output_json = convert_md_to_json("atlas.txt")
output_json_path = 'atlas_converted.json'
with open(output_json_path, 'w') as f:
    json.dump(output_json, f, indent=4)

output_json_path