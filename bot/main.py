import time
import schedule
import threading
from utils import *
from models import Base
from client import TelegramClient
from telebot import TeleBot, types
from telegram_bot_calendar import DetailedTelegramCalendar
from crud import create_task, update_task, view_tasks, delete_task, create_user
from loader import _, bot, i18n, logger, TOKEN, ADMIN_CHAT_ID, NOTIFICATION_FREQUENCY

CHOICE = ""


def init_menu(message: types.Message) -> None:
    """
    Initializes main(basic) menu.
    Args:
        message: User message.

    Returns:
        None
    """

    bot.send_message(message.chat.id, _("Please choose the action"), reply_markup=get_keyboard("base"))


def add_user_task(message: types.Message, **kwargs) -> None:
    """
    Creates new task for user on selected date. Calls crud.create_task function which performs operations
    on database.
    Args:
        message: User message.
        **kwargs: Used to receive the chosen date.

    Returns:
        None
    """

    bot.delete_message(message.chat.id, message.id-1)
    bot.delete_message(message.chat.id, message.id)
    if create_task(user_id=message.from_user.id, task=message.text.strip(), date=kwargs.get("date")):
        bot.send_message(message.chat.id, _("✅ The task successfully added!"), reply_markup=get_keyboard("back"))
    else:
        bot.send_message(message.chat.id, _("🤖 Whoops. Something went wrong"), reply_markup=get_keyboard("back"))


def update_user_task(message: types.Message, **kwargs) -> None:
    """
    Updates selected task. Calls crud.update_task function which performs operations
    on database.
    Args:
        message: User message.
        **kwargs: Used to receive the chosen task ID.

    Returns:
        None
    """

    if update_task(task_id=kwargs.get("task_id"), edited_task=message.text):
        bot.send_message(message.chat.id, _("✅ The task successfully updated!"), reply_markup=get_keyboard("back"))
    else:
        bot.send_message(message.chat.id, _("🤖 Whoops. Something went wrong"), reply_markup=get_keyboard("back"))


def update_user_timezone(message: types.Message) -> None:
    """
    Updates the user timezone. Calls utils.get_location function to get user coordinates by provided city,
    utils.get_timezone_by_location to get timezone by received coordinates and utils.update_timezone function which
    performs operations on database.
    Args:
        message: User message.

    Returns:
        None
    """

    location = get_location(message.text)
    if location is None:
        bot.reply_to(message,
                     _("🤖 I can't find the provided city. Try to specify a larger city nearby."),
                     reply_markup=get_keyboard("retry"))
    else:
        timezone, offset = get_timezone_by_location(location)
        if update_timezone(timezone_str=timezone, user_id=message.from_user.id):
            bot.send_message(message.chat.id, _("🕒 The timezone is set as {} (GMT {}).")
                             .format(timezone, offset), reply_markup=get_keyboard("back"))
        else:
            bot.send_message(message.chat.id, _("🤖 Whoops. Something went wrong"), reply_markup=get_keyboard("back"))


@bot.middleware_handler(update_types=["message", "callback_query"])
def set_context_language(bot_instance: TeleBot, message: types.Message) -> None:
    """
     This middleware handler is called when new updates are coming. It passes the current context language in
     I18N class.

    Args:
        bot_instance: TeleBot instance.
        message: User message.

    Returns:
        None
    """

    user = get_user(message.from_user.id)
    if user:
        user_language = user.language
    else:
        user_language = "ru"
    i18n.context_lang.language = user_language


@bot.message_handler(commands=["start", "help"])
def commands_handler(message: types.Message) -> None:
    """
    Handles commands /start and /help.
    If /start, generates the welcome message depending on user status (registered or new) and initializes main menu. If
    user is new, calls crud.create_user function to register it.
    If /help, sends help message.
    Args:
        message: User message.

    Returns:
        None
    """

    match message.text:
        case "/start":
            user = get_user(message.from_user.id)
            if user:
                bot.reply_to(message, _("👋 Welcome back, {}!").format(message.from_user.first_name))
                init_menu(message)
            else:
                create_user(telegram_user_id=message.from_user.id, telegram_user_name=message.from_user.first_name,
                            chat_id=message.chat.id)
                bot.reply_to(message, _("🤝 Welcome, {}!\n I'll help you not to forget the most important.").format(
                    message.from_user.first_name))
                init_menu(message)
        case "/help":
            bot.reply_to(message, get_help_text())
            init_menu(message)


@bot.callback_query_handler(func=lambda call: call.data in ["create", "read", "read_today", "update", "delete"])
def basic_menu_handler(call: types.CallbackQuery) -> None:
    """
    Handles user choice of "create", "read", "read_today", "update", "delete" commands in main menu (main.init_menu).
    If the command is "read_today" which means "view today tasks", calls crud.view_tasks function that generates the
    list of user tasks by date to send it to user. It also uses utils.get_user_date function to get the exact
    date in user timezone.
    If other commands are received, forwards user to date pick just because choosing the date is the first step of
    all this commands.
    Args:
        call: Callback query.

    Returns:
        None
    """

    global CHOICE
    CHOICE = call.data
    bot.delete_message(call.message.chat.id, call.message.id)
    if CHOICE == "read_today":
        bot.send_message(call.message.chat.id, view_tasks(user_id=call.from_user.id,
                                                          date=get_user_date(
                                                              timezone=get_user(
                                                                  user_id=call.from_user.id).timezone).date()),
                         reply_markup=get_keyboard("back"))
    else:
        calendar, step = DetailedTelegramCalendar().build()
        bot.send_message(call.message.chat.id, _("🤖 Ok! Let's choose the date"), reply_markup=calendar)


@bot.callback_query_handler(func=lambda call: call.data == "tz")
def timezone_menu_handler(call: types.CallbackQuery) -> None:
    """
    Handles user choice of "tz" command in main menu (main.init_menu).
    Args:
        call: Callback query.

    Returns:
        None
    """

    bot.delete_message(call.message.chat.id, call.message.id)
    text = _("🤖 Please tell me in which city are you located and I'll find the proper timezone automatically.\n"
             "The current timezone is:\n*{}*").format(get_user_timezone(call.message.chat.id))
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(call.message, update_user_timezone)


@bot.callback_query_handler(func=lambda call: call.data.startswith("time"))
def time_menu_handler(call: types.CallbackQuery) -> None:
    """
    Handles user action related to setting notification time including main menu button click, buttons that set start
    and end time, muting notifications if there are no active tasks and choosing particular time itself.
    Main menu button click calls utils.get_user_notification_time function to get current user time frames.
    If user choose the new time, utils.update_user_notifications function is called which performs
    operations on database.
    Args:
        call: Callback query.

    Returns:
        None
    """

    global CHOICE
    bot.delete_message(call.message.chat.id, call.message.id)
    match call.data:
        case "timeset":
            time_from, time_to = get_user_notification_time(user_id=call.from_user.id)
            muted = get_user(user_id=call.from_user.id).muted
            text = _("🤖 Here you can change the time frame during which bot will notify you about scheduled tasks. "
                     "This will be helpful to prevent bothering you during the night and other inappropriate time. "
                     "If you want to set notification once a day in a specific time, just choose the same start and "
                     "stop time."
                     "\n_The current time frame is:_\nStart at: *{}* \nStop at: *{}*").format(time_from, time_to)
            bot.send_message(call.message.chat.id, text, reply_markup=get_keyboard("clock_menu", muted=muted),
                             parse_mode="Markdown")
        case "time_from" | "time_to":
            CHOICE = call.data
            bot.send_message(call.message.chat.id, _("🤖 Please select the required time"),
                             reply_markup=get_keyboard("clock"))
        case "time_mute" | "time_unmute":
            if mute_user_notifications(user_id=call.from_user.id):
                bot.send_message(call.message.chat.id, _("🤖 Success"),
                                 reply_markup=get_keyboard("back"))
            else:
                bot.send_message(call.message.chat.id, _("🤖 Whoops. Something went wrong"),
                                 reply_markup=get_keyboard("back"))
        case _:
            user_time = call.data.removeprefix("time_")
            if update_user_notifications(user_id=call.from_user.id, choice=CHOICE, time=user_time):
                bot.send_message(call.message.chat.id, _("🤖 The time frame was successfully updated"),
                                 reply_markup=get_keyboard("back"))
            else:
                bot.send_message(call.message.chat.id, _("🤖 Whoops. Something went wrong"),
                                 reply_markup=get_keyboard("back"))


@bot.callback_query_handler(func=lambda call: call.data.startswith("lang"))
def language_menu(call: types.CallbackQuery) -> None:
    """
    Handles user action related to setting the preferred language. Calls utils.set_language function which performs
    operations on database.
    Args:
        call: Callback query.

    Returns:
        None
    """

    bot.delete_message(call.message.chat.id, call.message.id)
    match call.data:
        case "lang":
            bot.send_message(call.message.chat.id, _("🤖 Choose the language "),
                             reply_markup=get_keyboard("language"))
        case "lang_ru" | "lang_en":
            language = call.data.removeprefix("lang_")
            if set_language(language=language, user_id=call.from_user.id):
                match language:
                    case "ru":
                        bot.send_message(call.message.chat.id, "🇷🇺 Установлен русский язык!",
                                         reply_markup=get_keyboard("ok"))
                    case "en":
                        bot.send_message(call.message.chat.id, "🇺🇸 The language is set to English!",
                                         reply_markup=get_keyboard("ok"))
            else:
                bot.send_message(call.message.chat.id, _("🤖 Whoops. Something went wrong"),
                                 reply_markup=get_keyboard("back"))


@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call: types.CallbackQuery) -> None:
    """
    Initializes menu with "back" button.
    Args:
        call: Callback query.

    Returns:
        None
    """

    bot.delete_message(call.message.chat.id, call.message.id)
    init_menu(call.message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("del_") or call.data.startswith("upd_"))
def update_delete_user_task(call: types.CallbackQuery) -> None:
    """
    Handles user action related to updating or deleting user tasks on selected date.
    Regarding the delete operation crud.delete_task function is called which performs operations on database.
    Regarding the update operation updated tsk text is requested.
    Args:
        call: Callback query.

    Returns:
        None
    """

    prefix = call.data[:4]
    task_id = call.data[4:]
    bot.delete_message(call.message.chat.id, call.message.id)
    match prefix:
        case "del_":
            if delete_task(task_id=task_id):
                bot.send_message(call.message.chat.id, _("✅ The task successfully deleted!"),
                                 reply_markup=get_keyboard("back"))
            else:
                bot.send_message(call.message.chat.id, _("🤖 Whoops. Something went wrong"),
                                 reply_markup=get_keyboard("back"))
        case "upd_":
            bot.send_message(call.message.chat.id, _("🤖 Please provide the updated task"))
            bot.register_next_step_handler(call.message, update_user_task, task_id=task_id)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def crud_handler(call: types.CallbackQuery) -> None:
    """
    Handles actions after picking the date in main menu for CRUD operations. In "read" operation crud.view_tasks
    function is called to generate the list of user tasks by date and send it to user. In "delete" and "update"
    operations utils.get_task_list function is called to generate inline keyboard markup with user tasks by date.
    Args:
        call: Callback query.

    Returns:
        None
    """

    global CHOICE
    user = get_user(user_id=call.from_user.id)
    if user:
        locale = user.language
    else:
        locale = "ru"
    result, key, step = DetailedTelegramCalendar(current_date=datetime.datetime.now().date(),
                                                 locale=locale).process(call.data)
    if not result and key:
        bot.edit_message_text(_("🤖 Ok! Let's choose the date"), call.message.chat.id, call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        match CHOICE:
            case "create":
                bot.send_message(call.message.chat.id, _("🤖 Tell me, what you want to do this day?"))
                bot.register_next_step_handler(call.message, add_user_task, date=result)
            case "read":
                bot.send_message(call.message.chat.id, view_tasks(user_id=call.from_user.id, date=result),
                                 reply_markup=get_keyboard("back"))
            case "delete":
                markup, have_tasks = get_task_list(user_id=call.from_user.id, date=result, prefix="del")
                if have_tasks:
                    msg = _("🤖 Please choose the task to be deleted")
                else:
                    msg = _("🤖 There are no tasks on that date!")
                bot.send_message(call.message.chat.id, msg,
                                 reply_markup=markup)
            case "update":
                markup, have_tasks = get_task_list(user_id=call.from_user.id, date=result, prefix="upd")
                if have_tasks:
                    msg = _("🤖 Please choose the task to be updated")
                else:
                    msg = _("🤖 There are no tasks on that date!")
                bot.send_message(call.message.chat.id, msg,
                                 reply_markup=markup)


def send_notification() -> None:
    """
    Send messages via mailing list generated by calling utils.get_send_list function.
    Returns:
        None
    """

    send_list = get_send_list()
    logger.info(f"Starting mailing. Found {len(send_list)} relevant users")
    for user, user_tasks in send_list.items():
        bot.send_message(user, user_tasks)
        logger.info(f"Notification successfully sent to {user}")


def schedule_checker() -> None:
    """
    Worker for checking if notification time has come.
    Returns:
        None
    """

    while True:
        time.sleep(schedule.idle_seconds())
        schedule.run_pending()


if __name__ == "__main__":
    Base.metadata.create_all()
    admin_logger_client = TelegramClient(TOKEN)
    schedule.every(int(NOTIFICATION_FREQUENCY)).hours.at(":00").do(send_notification)
    while True:
        try:
            threading.Thread(target=schedule_checker).start()
            bot.polling()
        except Exception as e:
            log_message = f"{datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')} : {e.__class__}\n{e}"
            admin_logger_client.post(method="sendMessage", params={"chat_id": ADMIN_CHAT_ID, "text": log_message})
