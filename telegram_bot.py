import os
import random
import logging
import redis
from get_questions_from_file import get_questions_for_qiuz
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          RegexHandler, Filters,
                          CallbackContext, ConversationHandler)


def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_text('Привет! Я бот для викторин!',
                              reply_markup=reply_markup)
    return CHOOSING


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Вы можете получить новые вопросы, сдаться или \
                              посмотреть свой счёт с помощью кнопок меню.')


def handle_new_question_request(update: Update, context: CallbackContext):
    question = random.choice(questions_for_quiz)
    redis_db.set('tg-'+str(update.message.from_user['id']),
                 str(question['answer']))
    update.message.reply_text(f'Новый вопрос:\n{question["question"]}')
    return ANSWERING


def handle_solution_attempt(update: Update, context: CallbackContext):
    answer = redis_db.get('tg-'+str(update.message.from_user['id'])).decode("utf-8")
    breaking_points = ['.', '(', '-']
    for breaking_point in breaking_points:
        if breaking_point in answer:
            answer = answer[:answer.find(breaking_point)]
    if update.message.text.lower() == answer.lower():
        update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса\
                                  нажми «Новый вопрос»')
        return CHOOSING
    else:
        update.message.reply_text('Неправильно, пробуй ещё')
        return ANSWERING


def handle_give_up(update: Update, context: CallbackContext) -> None:
    answer = redis_db.get(update.message.from_user['id']).decode("utf-8")
    update.message.reply_text(f'Правильный ответ был:\n{answer}')
    handle_new_question_request(update, context)


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Команда заверщения викторины")
    return ConversationHandler.END


def main() -> None:
    CHOOSING, ANSWERING = range(2)
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счёт']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)
    updater = Updater(os.environ['TELEGRAM_TOKEN'])
    questions_for_quiz = get_questions_for_qiuz('./quiz_questions/lag01ch.txt')
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
                       handle_new_question_request)
                       ],
            ANSWERING: [MessageHandler(Filters.regex('^Сдаться$'),
                        handle_give_up),
                        MessageHandler(Filters.text,
                        handle_solution_attempt),
                        ],
        },

        fallbacks=[MessageHandler(Filters.regex('^/cancel$'),
                                  cancel, pass_user_data=True)]
    )
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
