import json

def load_settings(file_path:str) -> dict:
    '''
    loads settings from a JSON file and returns them as a dictionary
    '''
    with open(file_path, "r", encoding="utf-8") as file:
        settings = json.load(file)
    
    return settings

SETTINGS = load_settings("settings.json")
