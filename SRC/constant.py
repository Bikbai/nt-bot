import os

BOT_TOKEN = os.environ.get('BOT_TOKEN', 'MTAyMzAwNzQ4OTQ1ODk2NjU0OA.Gu7LyD.7keR7ott47PIXbB2_w7z0N3IbFR0mK-xFy-ULc')
#BOT_TOKEN = 'OTk5MjYwOTk3MTA3ODU5NTU2.GaT_Q9.hgcqiBvnSSIyru_TufIadXPtGMqVCf5EhxNFRE'
GUILD_LIST_URL = 'http://nordic-tribe.ru/guildlist.php'
GL_FILENAME = '../guild.txt'
TR_FILENAME = "../timeroles.json"

ADMIN_ROLE = os.environ.get('ADMIN_ROLE', "Администрация")
PLAYER_ROLE = os.environ.get("PLAYER_ROLE", "Участник")
UNCONFIRM_ROLE = os.environ.get("UNCONFIRM_ROLE",  "Неподтверждённые")
CHILL_ROLE = os.environ.get("CHILL_ROLE", 'Бронь')
BOT_ROLE = os.environ.get("BOT_ROLE", 'Bot')

#длительность роли
CHILL_ROLE_LENGTH = os.environ.get("CHILL_ROLE_LENGTH",  7*24*3600)