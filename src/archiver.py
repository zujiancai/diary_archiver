from common import DIARY_LABEL
from data_access import open_store

import gkeepapi


if __name__ == '__main__':
    # Login to Google Keep
    keep = gkeepapi.Keep()
    email = input('Google login email: ')
    password = input('Google password: ')
    keep.login(email, password)

    # Find all notes with label
    gnotes = keep.find(labels=[keep.findLabel(DIARY_LABEL)], archived=True, trashed=False)

    # Insert note data to Diaries and Tags tables
    with open_store() as store:
        note_count = 0
        tag_count = 0
        for note in gnotes:
            diary_id = store.upsert_diary(note.title, note.text, note.color.name)
            print('Archived note: {}'.format(note.title))
            note_count += 1
            for lbl in note.labels.all():
                if lbl.name != DIARY_LABEL:
                    store.upsert_tag(lbl.name, diary_id, 'Google Keep')
                    tag_count += 1

    print('Finished with {0} diaries and {1} tags.'.format(note_count, tag_count))
