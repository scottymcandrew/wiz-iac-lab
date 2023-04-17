import json
import copy

f_wizcli_output = open('wizcli-results.json')
wizcli_data = json.load(f_wizcli_output)
wiz_to_sarif_severity_map = {
    "INFORMATIONAL": "none",
    "LOW": "none",
    "MEDIUM": "note",
    "HIGH": "warning",
    "CRITICAL": "error"
}

sarif_base_template = {
    '$schema': 'https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json',
    'version': '2.1.0',
    'runs': [
        {
            'tool': {
                'driver': {
                    'name': 'Wiz',
                    'version': '0.1',
                    'informationUri': 'https://wiz.io',
                    'rules': [],
                    'organization': 'wiz'
                }
            },
            'results': []
        },
    ]
}

sarif_rule_template = {
    'id': '',
    'name': '',
    'shortDescription': {'text': ''},
    'fullDescription': {'text': ''},
    'help': {'text': ''},
    'defaultConfiguration': {'level': ''}
}

sarif_result_template = {
    'ruleId': '',
    'ruleIndex': 0,
    'level': '',
    'message': {'text': ''},
    'locations': [
        {
            'physicalLocation': {
                'artifactLocation': {'uri': ''},
                'region': {'startLine': 0}
            }
        }
    ]
}

# This is required, because Wiz-cli uses a nested array for triggered resources
# whereas Sarif has separate sections for rules and results
sarif_rule_index = 0
# Results index needs to be maintained as this is a separate list to rules
sarif_results_index = 0

for item in wizcli_data["result"]["ruleMatches"]:

    # Add new list entry for rule
    sarif_base_template['runs'][0]['tool']['driver']['rules'].append(copy.deepcopy(sarif_rule_template))

    # for index, item in enumerate(wizcli_data["result"]["ruleMatches"]):
    # Setting specific variables before applying to sarif template, in case they change in future
    rule_id = item["rule"]["id"]
    rule_description = item["rule"]["name"]
    sarif_severity = wiz_to_sarif_severity_map[item["severity"]]

    for item_x in wizcli_data["result"]["ruleMatches"][sarif_rule_index]["matches"]:
        # for index_x, item_x in enumerate(wizcli_data["result"]["ruleMatches"][index]["matches"]):
        # Setting specific variables
        resource_name = item_x["resourceName"]
        file_name = item_x["fileName"]
        line_number = item_x["lineNumber"]
        match_content = item_x["matchContent"]
        expected_config = item_x["expected"]
        found_config = item_x["found"]

        # Add new list entry for results
        sarif_base_template['runs'][0]['results'].append(copy.deepcopy(sarif_result_template))

        # Populate results
        sarif_base_template['runs'][0]['results'][sarif_results_index]['ruleId'] = rule_id
        sarif_base_template['runs'][0]['results'][sarif_results_index]['ruleIndex'] = sarif_rule_index
        sarif_base_template['runs'][0]['results'][sarif_results_index]['level'] = sarif_severity
        sarif_base_template['runs'][0]['results'][sarif_results_index]['message']['text'] = rule_description
        sarif_base_template['runs'][0]['results'][sarif_results_index]['locations'][0]['physicalLocation']['artifactLocation']['uri'] = file_name
        sarif_base_template['runs'][0]['results'][sarif_results_index]['locations'][0]['physicalLocation']['region']['startLine'] = line_number

        sarif_results_index += 1

    # Populate rule entry
    sarif_base_template['runs'][0]['tool']['driver']['rules'][sarif_rule_index]['id'] = rule_id
    sarif_base_template['runs'][0]['tool']['driver']['rules'][sarif_rule_index]['name'] = rule_description
    sarif_base_template['runs'][0]['tool']['driver']['rules'][sarif_rule_index]['shortDescription']['text'] = rule_description
    sarif_base_template['runs'][0]['tool']['driver']['rules'][sarif_rule_index]['fullDescription']['text'] = rule_description
    sarif_base_template['runs'][0]['tool']['driver']['rules'][sarif_rule_index]['help']['text'] = "Expected: " + expected_config + "  Found: " + found_config
    sarif_base_template['runs'][0]['tool']['driver']['rules'][sarif_rule_index]['defaultConfiguration']['level'] = sarif_severity

    sarif_rule_index += 1

print(json.dumps(sarif_base_template))

f_wizcli_output.close()