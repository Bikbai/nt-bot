import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
if BOT_TOKEN is None:
    raise Exception("Не задан секретный токен бота")
GUILD_LIST_URL = 'http://nordic-tribe.ru/guildlist.php'
GL_FILENAME = 'data/guild.txt'
TR_FILENAME = "data/timeroles.json"

ADMIN_ROLE = os.environ.get('ADMIN_ROLE', "Администрация")
PLAYER_ROLE = os.environ.get("PLAYER_ROLE", "Участник")
UNCONFIRM_ROLE = os.environ.get("UNCONFIRM_ROLE",  "Неподтверждённые")
CHILL_ROLE = os.environ.get("CHILL_ROLE", 'Бронь')
BOT_ROLE = os.environ.get("BOT_ROLE", 'Bot')
SLEEP_DELAY = os.environ.get("SLEEP_DELAY", 3600)
