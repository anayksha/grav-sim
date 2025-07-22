import json

def remove_comments(string:str, cmmt_mkr:str) -> str:
    '''
    recursive function that removes single line comments in a string
    '''
    if cmmt_mkr not in string:
        return string
    else:
        mkr_index = string.find(cmmt_mkr)
        return remove_comments(string[:mkr_index] + string[string.find("\n", mkr_index):], cmmt_mkr)

def load_settings(file_path:str) -> dict:
    '''
    loads settings from a JSON file and returns them as a dictionary
    '''
    with open(file_path, "r", encoding="utf-8") as file:
        json_raw = file.read()

    # need to remove comments from the settings json so it can be parsed
    # by the json library
    return json.loads(remove_comments(json_raw, "//"))

SETTINGS = load_settings("settings.json")
