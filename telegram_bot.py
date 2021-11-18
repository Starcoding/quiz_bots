import os
import random
import logging
import redis
from functools import partial
from answer_check import check_answer
from get_questions import get_questions_for_qiuz
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          RegexHandler, Filters,
                          CallbackContext, ConversationHandler)


logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text('Привет! Я бот для викторин!',
                              reply_markup=reply_markup)
    return CHOOSING


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Вы можете получить новые вопросы, сдаться или \
                              посмотреть свой счёт с помощью кнопок меню.')


def handle_new_question_request(update: Update, context: CallbackContext, questions_for_quiz, redis_db):
    question = random.choice(questions_for_quiz)
    redis_db.set(f'tg-{update.message.from_user["id"]}',
                 question['answer'])
    update.message.reply_text(f'Новый вопрос:\n{question["question"]}')
    return ANSWERING


def handle_solution_attempt(update: Update, context: CallbackContext, redis_db):
    answer = redis_db.get(f'tg-{update.message.from_user["id"]}').decode("utf-8")
    if update.message.text.lower() == check_answer(answer).lower():
        update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса\
                                  нажми «Новый вопрос»')
        return CHOOSING
    update.message.reply_text('Неправильно, пробуй ещё')
    return ANSWERING


def handle_give_up(update: Update, context: CallbackContext, questions_for_quiz, redis_db) -> None:
    answer = redis_db.get(f'tg-{update.message.from_user["id"]}').decode("utf-8")
    update.message.reply_text(f'Правильный ответ был:\n{answer}')
    handle_new_question_request(update, context, questions_for_quiz, redis_db)


def cancel(update: Update, context: CallbackContext, questions_for_quiz, redis_db):
    update.message.reply_text("Команда заверщения викторины")
    return ConversationHandler.END


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    CHOOSING, ANSWERING = range(2)
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счёт']]
    
    updater = Updater(os.environ['TELEGRAM_TOKEN'])
    questions_for_quiz = get_questions_for_qiuz(os.environ['PATH_TO_CATALOG'])
    redis_db = redis.Redis(host=os.environ['REDIS_HOST'],
                           port=os.environ['REDIS_PORT'],
                           db=0,
                           password=os.environ['REDIS_PASSWORD'])
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("help", help_command))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [MessageHandler(Filters.regex('^Новый вопрос$'),
                       partial(handle_new_question_request, questions_for_quiz=questions_for_quiz, redis_db=redis_db))
                       ],
            ANSWERING: [MessageHandler(Filters.regex('^Сдаться$'),
                        partial(handle_give_up, questions_for_quiz=questions_for_quiz, redis_db=redis_db)),
                        MessageHandler(Filters.text,
                        partial(handle_solution_attempt, redis_db=redis_db)),
                        ],
        },
        fallbacks=[MessageHandler(Filters.regex('^/cancel$'),
                                  cancel, pass_user_data=True)]
    )
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()
