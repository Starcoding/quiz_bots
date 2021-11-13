from os import listdir
from os.path import isfile, join

def get_questions_for_qiuz(catalog_name):
    questions = []
    files = [f for f in listdir(catalog_name) if isfile(join(catalog_name, f))]
    for file in files:
        with open(f'{catalog_name}/{file}', 'r', encoding='KOI8-R') as quiz_file:
            quiz_text = quiz_file.read()
        while quiz_text.find('Вопрос') > 0:
            question_start = quiz_text.find('Вопрос')
            colon_position_for_question = quiz_text.find(':\n', question_start) + 2
            question_end = quiz_text.find('\n\n', question_start)
            question = quiz_text[colon_position_for_question:question_end].replace('\n', ' ')
            answer_start = quiz_text.find('Ответ:', question_end)
            colon_position_for_answer = quiz_text.find(':\n', answer_start) + 2
            answer_end = quiz_text.find('\n\n', answer_start)
            answer = quiz_text[colon_position_for_answer:answer_end].replace('\n', ' ')
            quiz_text = quiz_text[answer_end:]
            questions.append({'question': question, 'answer': answer})
    return questions
