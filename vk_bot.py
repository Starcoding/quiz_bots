import os
import random
import vk_api as vk
import redis
from get_questions_from_file import get_questions_for_qiuz
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType


def send_message(user_id, message):
    vk_api.messages.send(
        user_id=user_id,
        message=message,
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1, 1000)
    )


def send_new_question(event, vk_api):
    question = random.choice(questions_for_quiz)
    redis_db.set('vk-'+str(event.user_id), str(question['answer']))
    send_message(event.user_id, f'Новый вопрос:\n{question["question"]}')


def give_up(event, vk_api):
    answer = redis_db.get(event.user_id).decode("utf-8")
    send_message(event.user_id, f'Правильный ответ был:\n{answer}')
    send_new_question(event, vk_api)


def handle_solution_attempt(event, vk_api):
    answer = redis_db.get('vk-'+str(event.user_id)).decode("utf-8")
    breaking_points = ['.', '(', '-']
    for breaking_point in breaking_points:
        if breaking_point in answer:
            answer = answer[:answer.find(breaking_point)]
    if event.text.lower() == answer.lower():
        send_message(event.user_id, 'Правильно! Поздравляю! Для следующего \
                     вопроса нажми «Новый вопрос»')
    else:
        send_message(event.user_id, 'Неправильно, пробуй ещё')


def main():
    questions_for_quiz = get_questions_for_qiuz('./quiz_questions/lag01ch.txt')
    redis_db = redis.Redis(host=os.environ['REDIS_HOST'],
                           port=os.environ['REDIS_PORT'],
                           db=os.environ['REDIS_DB'],
                           password=os.environ['REDIS_PASSWORD'])
    vk_session = vk.VkApi(token=os.environ['VK_TOKEN'])
    vk_api = vk_session.get_api()
    keyboard = VkKeyboard()
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.PRIMARY)

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == "Сдаться":
                give_up(event, vk_api)
            elif event.text == "Новый вопрос":
                send_new_question(event, vk_api)
            else:
                handle_solution_attempt(event, vk_api)

if __name__ == "__main__":
    main()
