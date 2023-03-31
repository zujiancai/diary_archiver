import base64
from datetime import datetime
import json
import os
import sqlite3


def base64_encode(utf8_data: str):
    return base64.b64encode(utf8_data.encode('utf-8')).decode('ascii')


class DataStore:
    def __init__(self, database_path: str, skip_create: bool):
        self.database_path = database_path
        self.skip_create = skip_create
        
    def __enter__(self):
        # Connect to SQLite database
        self.db = sqlite3.connect(self.database_path)

        # Create tables in case they don't already exist
        if not self.skip_create:
            self.create_tables()

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print('{0} - {1}: {2}'.format(exc_type, exc_value, exc_traceback))
        self.db.commit()
        self.db.close()

    def create_tables(self):
        with open('create_tables.sql', 'r') as f:
            query = f.read()

        cursor = self.db.cursor()
        cursor.executescript(query)

    def all_diaries(self):
        cursor = self.db.cursor()
        return cursor.execute("SELECT diary_id, title, content, color FROM Diaries")

    def update_color(self, diary_id: str, new_color: str):
        cursor = self.db.cursor()
        cursor.execute("UPDATE Diaries SET color=?, updated_time=? WHERE diary_id=?",
                        (new_color, datetime.now(), diary_id))

    def upsert_diary(self, title: str, content: str, color: str):
        cursor = self.db.cursor()

        # Generate a diary_id from the note title
        diary_id = base64_encode(title)

        # Check if the diary entry already exists
        cursor.execute("SELECT diary_id FROM Diaries WHERE diary_id=?", (diary_id,))
        result = cursor.fetchone()
        curr_time = datetime.now()
        if result and len(result) > 0:
            cursor.execute("UPDATE Diaries SET content=?, color=?, updated_time=? WHERE diary_id=?",
                            (content, color, curr_time, diary_id))
        else:
            cursor.execute("INSERT INTO Diaries (diary_id, title, content, color, inserted_time, updated_time) VALUES (?, ?, ?, ?, ?, ?)",
                            (diary_id, title, content, color, curr_time, curr_time))

        return diary_id

    def upsert_tag(self, tag_name: str, diary_id: str, source: str):
        cursor = self.db.cursor()

        # Generate a tag_id by joining tag_name and diary_id
        tag_id = '{0}_{1}'.format(base64_encode(tag_name), diary_id)

        # Check if the tag already exists for the diary entry
        cursor.execute("SELECT tag_id FROM Tags WHERE tag_id=?", (tag_id,))
        result = cursor.fetchone()
        curr_time = datetime.now()
        if result and len(result) > 0:
            cursor.execute("UPDATE Tags SET source=?, updated_time=? WHERE tag_id=?",
                            (source, curr_time, tag_id))
        else:
            cursor.execute("INSERT INTO Tags (tag_id, tag_name, diary_id, source, inserted_time, updated_time) VALUES (?, ?, ?, ?, ?, ?)",
                            (tag_id, tag_name, diary_id, source, curr_time, curr_time))


# Read configuration values from config.json file
# config_path = 'config.json'
config_path = '..\\..\\diary_archiver.config.json' # keep config file outside of this repo as having access key
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

DATABASE_PATH = config['database']
DIARY_LABEL = config['diary_label']
OPENAI_KEY = config['openai_key']


def open_store(skip_create: bool = False):
    return DataStore(DATABASE_PATH, skip_create)
