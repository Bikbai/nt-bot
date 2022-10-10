import os
from enum import Enum

BOT_TOKEN = os.environ.get('BOT_TOKEN')
if BOT_TOKEN is None:
    raise Exception("Не задан секретный токен бота")
GUILD_LIST_URL = 'http://nordic-tribe.ru/guildlist.php'
GL_FILENAME = 'data/guild.txt'
TR_FILENAME = "data/timeroles.json"
RIGHTS_FILENAME = "data/rights.json"
SLEEP_DELAY = os.environ.get("SLEEP_DELAY", 3600)

# константы, определяющие названия ролей
class RolesEnum(Enum):
    ADMIN_ROLE = 'Администрация'
    PLAYER_ROLE = 'Участник'
    UNCONFIRM_ROLE = 'Неподтверждённые'
    BOT_ROLE = 'Bot'
    REQRUITER_ROLE = 'Рекрутеры'
    NEWBIE_ROLE = 'Новичок'
    TRIAL_ROLE = 'Таймаут вступления'
    CHILL_ROLE = 'Чилл'