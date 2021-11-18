import os
import random
import vk_api as vk
import redis
from functools import partial
from answer_check import check_answer
from get_questions import get_questions_for_qiuz
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType


def send_message(user_id, message):
    vk_api.messages.send(
        user_id=user_id,
        message=message,
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1, 1000)
    )


def send_new_question(event, vk_api, questions_for_quiz, redis_db):
    question = random.choice(questions_for_quiz)
    redis_db.set(f'vk-{event.user_id}', question['answer'])
    send_message(event.user_id, f'Новый вопрос:\n{question["question"]}')


def give_up(event, vk_api, questions_for_quiz, redis_db):
    answer = redis_db.get(f'vk-{event.user_id}').decode("utf-8")
    send_message(event.user_id, f'Правильный ответ был:\n{answer}')
    send_new_question(event, vk_api, questions_for_quiz, redis_db)


def handle_solution_attempt(event, vk_api, redis_db):
    answer = redis_db.get(f'vk-{event.user_id}').decode("utf-8")
    if event.text.lower() == check_answer(answer).lower():
        send_message(event.user_id, 'Правильно! Поздравляю! Для следующего \
                     вопроса нажми «Новый вопрос»')
    else:
        send_message(event.user_id, 'Неправильно, пробуй ещё')


if __name__ == "__main__":
    questions_for_quiz = get_questions_for_qiuz(os.environ['PATH_TO_CATALOG'])
    redis_db = redis.Redis(host=os.environ['REDIS_HOST'],
                           port=os.environ['REDIS_PORT'],
                           db=0,
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
                give_up(event, vk_api, questions_for_quiz, redis_db)
            elif event.text == "Новый вопрос":
                send_new_question(event, vk_api, questions_for_quiz, redis_db)
            else:
                handle_solution_attempt(event, vk_api, redis_db)
