import re
from common import OPENAI_KEY, validate_keyword
from data_access import open_store

import openai


openai.api_key = OPENAI_KEY


def generate_keywords(content: str):
    prompt_text = 'Extract keywords from this text:\n\n' + content
    response = openai.Completion.create(
        model='text-davinci-003',
        prompt=prompt_text,
        temperature=0.5,
        max_tokens=60,
        top_p=1.0,
        frequency_penalty=0.8,
        presence_penalty=0.0
    )
    # need to handle utf-8 delimiters
    output = re.split('[:：]+', response.choices[0].text.strip())
    output = output[1] if len(output) > 1 else output[0]
    keywords = [ kw.strip() for kw in re.split('[,.，。]+', output) ] # expect output as "Keywords: k1, k2, ..., kn."
    return [ kw for kw in keywords if validate_keyword(kw) ] # remove short items, all digits length > 3, other string length > 1


def generate_color(content: str):
    prompt_text = content + ':\n\nbackground-color: #'
    response = openai.Completion.create(
        model='text-davinci-003',
        prompt=prompt_text,
        temperature=0,
        max_tokens=10,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=[";"]
    )
    output = response.choices[0].text.strip().split(';')
    return output[0]


if __name__ == '__main__':
    # Update color for diaries or create new tags by OpenAI
    with open_store(True) as store:
        color_count = 0
        tag_count = 0
        for row in store.all_diaries(): # row schema: diary_id, title, content, color
            diary_id, title, content, color = row
            new_color = generate_color(content)
            if new_color != color:
                store.update_color(diary_id, new_color)
                print('Updated color for {0}: {1} -> {2}'.format(title, color, new_color))
                color_count += 1
            for kw in generate_keywords(content):
                store.upsert_tag(kw, diary_id, 'OpenAI GPT-3')
                print('Added tag for {0}: {1}'.format(title, kw))
                tag_count += 1

    print('Finished with {0} color updates and {1} tags.'.format(color_count, tag_count))
