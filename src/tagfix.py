import re
from common import TAG_DELIMITERS, validate_keyword
from data_access import open_store


if __name__ == '__main__':
    SOURCE_NAME = 'tagfix'
    with open_store(True) as store:
        fix_count = 0
        tag_count = 0
        for delimiter in TAG_DELIMITERS: 
            for row in store.tags_contain(delimiter).fetchall(): # row schema: tag_id, tag_name, diary_id
                tag_id, tag_name, diary_id = row
                first_one = True
                for kw in tag_name.split(delimiter):
                    kw = kw.strip()
                    if validate_keyword(kw):
                        if first_one:
                            store.update_tag_name(tag_name, kw, SOURCE_NAME)
                            first_one = False
                            fix_count += 1
                            print('Fix tag {0}: {1} -> {2}'.format(tag_id, tag_name, kw))
                        else:
                            store.upsert_tag(kw, diary_id, SOURCE_NAME)
                            tag_count += 1
                            print('Added tag for {0}: {1}'.format(diary_id, kw))
    print('Finished with {0} tags fixed and {1} tags created.'.format(fix_count, tag_count))
