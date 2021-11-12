# quiz_bots
В данном проекте присутствует два бота: бот для Vkontakte и бот для Telegram.  
Пользователь может попросить у бота вопрос и попытаться на него ответить.  
В случае если ответ был верным - предложит пользователю получить ещё один вопрос.  
В случае если ответ неверный - бот попросит попробовать ещё раз.  
Пользователь может сдаться, получить правильный ответ и сразу новый вопрос.  
*примечание: для получения вопросов в Telegram, необходимо прописать команду /start*

## Деплой
Боты размещены на площадке Heroku.

## Демо версии
[Ссылка на группу ВК](https://vk.com/club208778943)  
[Ссылка на телеграм бота](https://t.me/dvmn_lesson_quiz_bot)


## Развертывание проекта
- Создайте базу данных [Redis](https://app.redislabs.com/). Вы получите адрес базы данных вида: ```redis-13965.f18.us-east-4-9.wc1.cloud.redislabs.com```, его порт вида: ```16635``` и его пароль.  
- *опционально:* создайте группу Вк и бота в telegram, чтобы получить токены  
Пропишите переменные окружения  
- ```REDIS_HOST``` - например ```redis-13965.f18.us-east-4-9.wc1.cloud.redislabs.com```
- ```REDIS_PORT``` - порт для подключения к Redis, например ```16635```
- ```REDIS_PASSWORD``` - пароль от вашей базы данных Redis
- ```TELEGRAM_TOKEN``` - токен для вашего телеграм бота
- ```VK_API_KEY``` - токен для группы ВК
- ```PATH_TO_FILE``` - путь к файлу с вопросами, например ```'./quiz_questions/lag01ch.txt'``` (*подробнее в конце Readme*)  

```pip install -r requirements.txt``` установит необходимые библиотеки  

Запустите любого бота:
- ```python3 vk_bot.py```
- ```python3 telegram_bot.py```

## Вопросы для опросника
Файлы с вопросами находятся в папке ```/quiz_questions```.  
Для добавления новых вопросов, вы можете скачать их [отсюда](https://dvmn.org/media/modules_dist/quiz-questions.zip). 
Поместив файл в папку, вы можете использовать его в ботах - нужно только прописать путь до файла в качестве переменной окружения.  
