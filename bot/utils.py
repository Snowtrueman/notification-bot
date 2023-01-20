import pytz
import geopy
import datetime
from loader import logger
from crud import get_tasks
from geopy import Location
from loader import _, session
from models import ToDos, Users
from sqlalchemy import exc, and_
from keyboards import get_keyboard
from timezonefinder import TimezoneFinder
from telebot.types import InlineKeyboardMarkup


def get_help_text() -> str:
    """
    Generates help text.
    Returns:
        Help text.
    """

    return _("This is the notification bot that'll help you not to forget the most important things. "
             "You can add, delete, edit tasks on a selected date and get quick access to the today's tasks. "
             "Bot will send you notifications about scheduled tasks every hour. You can change your timezone and time "
             "frame during which bot will notify you about scheduled tasks. This will be helpful to prevent bothering "
             "you during the night and other inappropriate time. You can choose between English and Russian language.")


def get_task_list(user_id: int, date: datetime.date, prefix: str) -> tuple[InlineKeyboardMarkup, bool]:
    """
    Generates inline keyboard markup with user tasks by date and indicates if the task list is empty or not.
    Args:
        user_id: User ID.
        date: Selected date.
        prefix: Prefix ("del_", "upd_") used in generating inline markup with task list. It's used in
        main.update_delete_user_task function to define user action via callback data.

    Returns:
        Inline keyboard markup with user tasks by date and boolean "True" if success, else inline keyboard with "back"
        button and boolean "False" if not.
    """

    tasks = get_tasks(user_id, date)
    markup = get_keyboard("tasks", tasks=tasks, prefix=prefix)
    if tasks:
        return markup, True
    else:
        return markup, False


def get_user(user_id: int) -> Users | None:
    """
    Returns user object by specified user ID.
    Args:
        user_id: User ID.

    Returns:
        User object if found else None.
    """

    user = session.query(Users).filter(Users.telegram_user_id == user_id).one_or_none()
    if user:
        return user
    else:
        return None


def get_user_date(timezone: str) -> datetime:
    """
    Returns the exact date in user timezone according to provided timezone.
    Args:
        timezone: User timezone.

    Returns:
        Date in user timezone.
    """

    source_date_with_timezone = pytz.timezone("Europe/London").localize(datetime.datetime.utcnow())
    target_date_with_timezone = source_date_with_timezone.astimezone(pytz.timezone(timezone))
    return target_date_with_timezone


def get_send_list() -> dict:
    """
    Generates dict of actual users to send notifications to.

    Returns:
        Dictionary with user Telegram chat ID as key and user task list as value.
    """

    users = session.query(Users).all()
    send_list = {}

    for user in users:
        target_date_with_timezone = get_user_date(user.timezone)

        user_date = target_date_with_timezone.date()
        user_time = target_date_with_timezone.time()

        if user.notifications_from <= user_time <= \
                (datetime.datetime.combine(datetime.date.today(), user.notifications_to)
                 + datetime.timedelta(minutes=2)).time():

            tasks = session.query(ToDos.todo).filter(and_(ToDos.user_id == user.id, ToDos.todo_date == user_date)).all()

            welcome_msg = "🤖 Привет, {}! Сегодня у нас по плану: \n".format(user.telegram_user_name)
            no_tasks = "🤖 Привет, {}! Я тут, чтобы сообщить, " \
                       "что запланированных дел на сегодня нет!".format(user.telegram_user_name)

            if user.language == "en":
                welcome_msg = "🤖 Hello, {}! Today we are going to:\n".format(user.telegram_user_name)
                no_tasks = "🤖 Hello, {}! I'm glad to inform you " \
                           "that there are no scheduled tasks today!".format(user.telegram_user_name)

            if len(tasks) != 0:
                msg = welcome_msg
                i = 1
                for task in tasks:
                    msg += f"{i}. {task[0]} \n"
                    i += 1
            else:
                if not user.muted:
                    msg = no_tasks
                else:
                    continue
            send_list[user.chat_id] = msg

    return send_list


def get_location(city: str) -> Location | None:
    """
    Returns user coordinates by provided city.
    Args:
        city: User city.

    Returns:
        Location object if success, else None.
    """

    geo = geopy.geocoders.Nominatim(user_agent="Notification_Bot")
    location = geo.geocode(city)
    return location


def get_timezone_by_location(location: Location) -> tuple[str, str]:
    """
    Returns timezone by provided coordinates.
    Args:
        location: Location object.

    Returns:
        Timezone and UTC offset.
    """

    time_zone_finder = TimezoneFinder()
    timezone_str = time_zone_finder.timezone_at(lng=location.longitude, lat=location.latitude)
    offset = datetime.datetime.now(tz=pytz.timezone(timezone_str)).strftime("%z")
    offset = offset[0:3] + ":" + offset[3:]
    return timezone_str, offset


def update_timezone(timezone_str: str, user_id: int) -> bool:
    """
    Performs operations on database to update user timezone.
    Args:
        timezone_str: User timezone.
        user_id: User ID.

    Returns:
        True if success else False.
    """

    user = get_user(user_id=user_id)
    if user:
        try:
            user.timezone = timezone_str
            session.add(user)
            session.commit()
            logger.info(f"User {user.telegram_user_id} successfully changed timezone to {timezone_str}")
            return True
        except exc.SQLAlchemyError:
            logger.error(f"Database error while changing {user.telegram_user_id}'s timezone to {timezone_str}")
            return False
    else:
        logger.error(f"Can't find user with telegram ID {user_id} in DB while changing timezone to {timezone_str}")
        return False


def set_language(language: str, user_id: int) -> bool:
    """
    Performs operations on database to set user language.
    Args:
        language: User language.
        user_id: User ID.

    Returns:
        True if success else False.
    """

    user = get_user(user_id=user_id)
    if user:
        try:
            user.language = language
            session.add(user)
            session.commit()
            logger.info(f"User {user.telegram_user_id} successfully changed language to {language}")
            return True
        except exc.SQLAlchemyError:
            logger.error(f"Database error while changing {user.telegram_user_id}'s language to {language}")
            return False
    else:
        logger.error(f"Can't find user with telegram ID {user_id} in DB while changing language to {language}")
        return False


def mute_user_notifications(user_id: int) -> bool:
    """
    Performs operations on database to disable or activate notifications if there are no active tasks.
    Args:
        user_id: User ID.

    Returns:
        True if success else False.
    """

    user = get_user(user_id=user_id)
    muted = False
    if user:
        try:
            if not user.muted:
                muted = True
            user.muted = muted
            session.add(user)
            session.commit()
            logger.info(f"User {user.telegram_user_id} successfully set muted notification to {muted} ")
            return True
        except exc.SQLAlchemyError:
            logger.error(f"Database error while setting {user.telegram_user_id}'s muted notification to {muted}")
    else:
        logger.error(f"Can't find user with telegram ID {user_id} in DB while setting muted notification to {muted}")
        return False


def update_user_notifications(user_id: int, choice: str, time: str) -> bool:
    """
    Performs operations on database to update user notification time.
    Args:
        user_id: User ID.
        choice: Time frame to update ("time_from" or "time_to").
        time: Selected time.

    Returns:
        True if success else False.
    """

    user = get_user(user_id=user_id)
    new_time = datetime.datetime.strptime(time, "%H:%M")
    if user:
        try:
            if choice == "time_from":
                user.notifications_from = new_time.time()
            elif choice == "time_to":
                user.notifications_to = new_time.time()
            session.add(user)
            session.commit()
            logger.info(f"User {user.telegram_user_id} successfully changed notification {choice} "
                        f"to {new_time.time()}")
            return True
        except exc.SQLAlchemyError:
            logger.error(f"Database error while changing {user.telegram_user_id}'s notification {choice} "
                         f"to {new_time.time()}")
            return False
    else:
        logger.error(f"Can't find user with telegram ID {user_id} in DB while changing notification {choice} "
                     f"to {new_time.time()}")
        return False


def get_user_notification_time(user_id: int) -> list:
    """
    Returns current user time frames.
    Args:
        user_id: User ID.

    Returns:
        List if user time frames ["time_from" , "time_to"]
    """

    user = get_user(user_id)
    return [user.notifications_from, user.notifications_to]


def get_user_timezone(user_id: int) -> str:
    """
    Returns user timezone.
    Args:
        user_id: USer ID.

    Returns:
        User timezone.
    """

    user = get_user(user_id)
    return user.timezone
