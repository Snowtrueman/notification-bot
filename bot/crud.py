import datetime
from sqlalchemy import exc
from sqlalchemy import and_
from models import Users, ToDos
from loader import _, logger, session


def get_tasks(user_id: int, date: datetime.date) -> dict | None:
    """
    Generates the dict of numbered tasks by provided user_id date or None if there are no tasks on that date.
    Args:
        user_id: User ID.
        date: Required date.

    Returns:
        The dict of numbered tasks or None.
    """

    data = {}
    tasks = session.query(ToDos.id, ToDos.todo).join(Users) \
        .filter(and_(Users.telegram_user_id == user_id, ToDos.todo_date == date)).all()
    if len(tasks) != 0:
        i = 1
        for task in tasks:
            clean_id, clean_task, *_ = task
            data[i] = {"id": clean_id, "task": clean_task}
            i += 1
        return data
    else:
        return None


def view_tasks(user_id: int, date: datetime.date) -> str:
    """
    Generates the answer message to user consisting of numbered tasks by provided user_id date or "No tasks" message.
    It calls crud.get_tasks function that creates the raw dict with tasks.
    Args:
        user_id: User ID.
        date: Required date.

    Returns:
        The string of numbered tasks or "No tasks" message.
    """

    msg = ""
    tasks = get_tasks(user_id=user_id, date=date)
    if tasks:
        for number, task in tasks.items():
            msg += f"{number}. {task['task']} \n"
        return msg
    else:
        return _("🤖 Wow! There are no tasks on that date!")


def create_task(user_id: int, task: str, date: str) -> bool:
    """
    Performs operations on database to creates new task for user on selected date.
    Args:
        user_id: User ID.
        task: User task.
        date: Scheduled date.

    Returns:
        True if success else False.
    """

    try:
        task = ToDos(
            user_id=session.query(Users.id).filter(Users.telegram_user_id == user_id).scalar(),
            todo=task,
            todo_date=date
        )
        session.add(task)
        session.commit()
        logger.info(f"User {user_id} successfully scheduled new task on {date}")
        return True
    except exc.SQLAlchemyError:
        logger.error(f"Database error while adding new task **{task}** for {user_id} on {date}")
        return False


def update_task(task_id: int, edited_task: str) -> bool:
    """
    Performs operations on database to update selected task.
    Args:
        task_id: ID of the task.
        edited_task: Edited task text.

    Returns:
        True if success else False.
    """

    try:
        task = session.query(ToDos).filter(ToDos.id == task_id).one_or_none()
        if task:
            task.todo = edited_task
            session.add(task)
            session.commit()
            logger.info(f"Task with ID {task_id} was successfully updated")
            return True
        else:
            logger.error(f"Can't find task with ID {task_id} in DB while updating it")
            return False
    except exc.SQLAlchemyError:
        logger.error(f"Database error while updating task with ID {task_id}")
        return False


def delete_task(task_id: str) -> bool:
    """
    Performs operations on database to delete selected task.
    Args:
        task_id: ID of the task.

    Returns:
        True if success else False.
    """

    try:
        task = session.query(ToDos).filter(ToDos.id == task_id).one_or_none()
        if task:
            session.delete(task)
            session.commit()
            logger.info(f"Task with ID {task_id} was successfully deleted")
            return True
        else:
            logger.error(f"Can't find task with ID {task_id} in DB while delete it")
            return False
    except exc.SQLAlchemyError:
        logger.error(f"Database error while deleting task with ID {task_id}")
        return False


def create_user(telegram_user_id: int, telegram_user_name: str, chat_id: int) -> bool:
    """
    Performs operations on database to create new user.
    Args:
        telegram_user_id: User ID in Telegram.
        telegram_user_name: Username in Telegram.
        chat_id: Chat ID in Telegram.

    Returns:
        True if success else False.
    """

    try:
        user = Users(
            telegram_user_id=telegram_user_id,
            telegram_user_name=telegram_user_name,
            chat_id=chat_id
        )
        session.add(user)
        session.commit()
        logger.info(f"Successfully registered new user with telegram ID {telegram_user_id}")
        return True
    except exc.SQLAlchemyError:
        logger.error(f"Database error while registering new user with telegram ID {telegram_user_id}")
        return False
