from os import listdir
from os.path import isfile, join

def get_questions_for_qiuz(catalog_name):
    questions = []
    files = [f for f in listdir(catalog_name) if isfile(join(catalog_name, f))]
    for file in files:
        print(file)
        with open(f'{catalog_name}/{file}', 'r', encoding='KOI8-R') as quiz_file:
            quiz_text = quiz_file.read()
        text_blocks = quiz_text.split('\n\n')
    for pos, text_block in enumerate(text_blocks):
        if 'Вопрос ' in text_block:
            question = text_block[text_block.find(':\n')+2:].replace('\n', ' ')
            answer = text_blocks[pos+1][text_blocks[pos+1].find(':\n')+2:]
            questions.append({'question': question, 'answer': answer})
    return questions