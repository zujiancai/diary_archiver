import json


# Read configuration values from config.json file
# config_path = 'config.json'
config_path = '..\\..\\diary_archiver.config.json' # keep config file outside of this repo as having access key
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

DATABASE_PATH = config['database']

DIARY_LABEL = config['diary_label']

OPENAI_KEY = config['openai_key']

TAG_DELIMITERS = config['tag_delimiters']


def validate_keyword(keyword: str):
    return len(keyword) > 3 or (not keyword.isdigit() and len(keyword) > 1)