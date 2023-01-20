# Telegram notification bot
Это бот для ежедневных напоминаний о вещах, которые необходимо не забыть сделать. 
Вы можете добавлять, удалять, редактировать дела на определённую дату, быстро просматривать список дел на сегодня. 
Бот будет напоминать вам о наличии запланированных дел каждый час. Для того чтобы бот не беспокоил по ночам и в 
прочее неподходящее время, предусмотрен механизм установки часового пояса пользователя по его местоположению, 
а также редактирования времени отправки напоминаний. 
В случае, если текущих дел на дату нет, бот все равно будет напоминать о своем существовании. 
Вы можете отключить или включить вновь такое поведение с помощью соответствующего пункта в меню. 
Также для вашего удобства, реализована интернационализация. Вы можете выбрать между двумя языками 
интерфейса - русским и английским.

[https://t.me/RemindMeSirBot](https://t.me/RemindMeSirBot)


### Стуктура проекта:
### main.py:
+ Основной модуль проекта;
+ Основные message и callback обработчики;
+ Планировщик рассылки уведомлений.

### loader.py:
+ Инициализация логгера;
+ Чтение необходимых переменных окружения из `.env` файла;
+ Инициализация прочих, необходимых для работы приложения, переменных.

### db.py
+ Создание подключения к БД;
+ Создание сессии.

### models.py:
+ Описание моделей БД `Users`, описывающей пользователей и `ToDos`, описывающей запланированные задания.

### crud.py:
+ CRUD операции с БД: регистрация пользователя, создание, просмотр, удаление обновление заданий.

### utils.py:
+ Различные вспомогательные функции, такие как поиск координат и установление временной зоны по названию города, 
формирование списка для рассылки уведомлений, установление времени оповещения, включения/отключения уведомлений в случае
отсутствующих задач и другие.

### client.py:
+ Простой Telegram-клиент, в функции которого входит отправка в чат администратору бота сообщений о критических сбоях в 
работе бота.

### keyboards.py:
+ Генерация всех inline-клавиатур в проекте.

### i18n_class.py:
+ Реализация интернационализации.

### .env:
+ Хранит переменные окружения: токен бота, чат ID администратора бота, частоту рассылки уведомлений
(по умолчанию - раз в час).


### Комментарии по установке:
**Необходимо обратить внимание на следующее:**
+ В проекте используется Python 3.10;
+ В `.env` файле должны быть определены 3 переменных: `BOT_TOKEN`, `ADMIN_TELEGRAM_ID`, `NOTIFICATION_FREQUENCY`;
+ В db.db необходимо проверить, и при необходимости задать путь к файлу БД `db_directory` и его имя `db_name`;
+ В loader.py при инициализации класса интернационализации I18N проверить, и при необходимости задать путь к 
файлам с переводами `translations_path`;
+ Пример docker-файл прилагается;
+ При запуске контейнера необходимо задать volumes для БД и логгера, чтобы иметь возможность сохранять состояние БД и 
историю событий в лог-файлах при остановке и перезапуске контейнера.




# Telegram notification bot
This is the notification bot that'll help you not to forget the most important things. You can add, delete, edit 
tasks on a selected date and get quick access to the today's tasks. Bot will send you notifications about scheduled 
tasks every hour. You can change your timezone (automatically by user location) and time frame during which bot will 
notify you about scheduled tasks. If there are no active tasks, bot will anyway inform about it. To change this action  
you can mute or unmute such notifications via choosing the required option in menu.
This will be helpful to prevent bothering you during the night and other inappropriate time. 
You can choose between English and Russian language.

[https://t.me/RemindMeSirBot](https://t.me/RemindMeSirBot)


### Project structure:
### main.py:
+ Main module;
+ Include main message and callback handlers;
+ Notification scheduler.

### loader.py:
+ Logger initialization;
+ Loading variables found as environment variables in `.env` file;
+ Initialization of other variables.

### db.py
+ Creates connection to database;
+ Creates session.

### models.py:
+ Contains models `Users`, and `ToDos`.

### crud.py:
+ CRUD operations such as user registrations, creating, reading, deleting and updating user tasks.

### utils.py:
+ Auxiliary tools such as getting timezone by user city, generating list of actual users to send notifications to,
setting the notification time, muting or unmuting notifications and other.

### client.py:
+ Simple Telegram client to send critical error messages to bot admin when exceptions happen.

### keyboards.py:
+ Generates all inline keyboards used in project.

### i18n_class.py:
+ Provides tool for internationalization.

### .env:
+ Stores such environment variables as: bot token, admin chat ID, notification frequency (by default - once an hour).


### Комментарии по установке:
**Please pay attention to the following:**
+ Python 3.10 required;
+ You should define 3 environment variables in `.env` file: `BOT_TOKEN`, `ADMIN_TELEGRAM_ID`, `NOTIFICATION_FREQUENCY`;
+ You should define the path to database file `db_directory` and its name `db_name` in `db.py`;
+ You should define path to translations `translations_path` in `loader.py`;
+ A docker file example is attached;
+ When running a docker container you should set docker volumes for database and log directories to save db and log 
history when stopping and restarting containers.