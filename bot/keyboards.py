from loader import _
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_keyboard(keyboard_type: str, tasks: dict = None, prefix: str = None, muted: bool = None) \
        -> InlineKeyboardMarkup:
    """
    Generates different keyboards according to "keyboard_type".
    Args:
        keyboard_type: Required keyboard type.
        tasks: Dict used to generate inline markup with task list.
        prefix: Prefix ("del_", "upd_") used in generating inline markup with task list. It's used in
        main.update_delete_user_task function to define user action via callback data.
        muted: Flag muted is used to properly generate "Mute"/"Unmute" buttons.

    Returns:
        Inline keyboard markup.
    """

    match keyboard_type:
        case "base":
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(InlineKeyboardButton(_("π View today tasks"), callback_data="read_today"))
            markup.add(InlineKeyboardButton(_("π View tasks by date"), callback_data="read"))
            markup.add(InlineKeyboardButton(_("β Add new task"), callback_data="create"))
            markup.add(InlineKeyboardButton(_("π Update task"), callback_data="update"))
            markup.add(InlineKeyboardButton(_("π Delete task"), callback_data="delete"))
            markup.add(InlineKeyboardButton(_("π Change timezone"), callback_data="tz"))
            markup.add(InlineKeyboardButton(_("π Change notification time frame"), callback_data="timeset"))
            markup.add(InlineKeyboardButton(_("π·πΊ|πΊπΈ ΠΠ·ΠΌΠ΅Π½ΠΈΡΡ ΡΠ·ΡΠΊ"), callback_data="lang"))

        case "back":
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(InlineKeyboardButton(_("β€΅οΈ Back"), callback_data="back"))

        case "ok":
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(InlineKeyboardButton(_("π Ok"), callback_data="back"))

        case "language":
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(InlineKeyboardButton("π·πΊ Π ΡΡΡΠΊΠΈΠΉ", callback_data="lang_ru"))
            markup.add(InlineKeyboardButton("πΊπΈ English", callback_data="lang_en"))
            markup.add(InlineKeyboardButton(_("β€΅οΈ Back"), callback_data="back"))

        case "retry":
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(InlineKeyboardButton(_("π Try again"), callback_data="tz"))

        case "tasks":
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            if tasks:
                for number, task in tasks.items():
                    markup.add(InlineKeyboardButton(task["task"], callback_data=f"{prefix}_{task['id']}"))
            markup.add(InlineKeyboardButton(_("β€΅οΈ Back"), callback_data="back"))

        case "clock":
            markup = InlineKeyboardMarkup()
            btns = []
            for i in range(24):
                hour = i if i >= 10 else f"0{i}"
                time = f"{hour}:00"
                btns.append(InlineKeyboardButton(time, callback_data=f"time_{time}"))
                if len(btns) == 4:
                    markup.row(*btns)
                    btns.clear()
            markup.row(*btns)
            markup.row(InlineKeyboardButton(_("β€΅οΈ Back"), callback_data="back"))

        case "clock_menu":
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(InlineKeyboardButton(_("ποΈ Set the start time"), callback_data="time_from"))
            markup.add(InlineKeyboardButton(_("π Set the stop time"), callback_data="time_to"))
            if muted:
                markup.add(InlineKeyboardButton(_("π Unmute notifications if no tasks"), callback_data="time_unmute"))
            else:
                markup.add(InlineKeyboardButton(_("π Mute notifications if no tasks"), callback_data="time_mute"))
            markup.add(InlineKeyboardButton(_("β€΅οΈ Back"), callback_data="back"))
    return markup
