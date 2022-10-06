import datetime
from typing import Optional

import jsonpickle
import os
import time
import json
from array import array

import discord.types.member
from attr import dataclass

import constant as c
from colorama import init, Back, Fore, Style
from discord.utils import get
from discord.ext import commands
import urllib.request
import utility as u


class GuildMember:
    gMemberName = ""
    dcUserName = ""


@dataclass
class TimeRole:
    userId: int
    roleId: int
    endDate: float
    userName: Optional[str]


class Roles:
    admin_role_id = 0
    player_role_id = 0
    unconfirmed_role_id = 0
    chill_role_id = 0
    bot_role_id = 0


class GGuild:
    __guild_list = dict()
    __bot = commands.Bot
    dc_roles = Roles()
    timed_roles: [TimeRole] = []

    def fill_guildlist(self):
        self.__guild_list.clear()
        u.log_info('Читаем список мемберов с сайта')
        urllib.request.urlretrieve(c.GUILD_LIST_URL, c.GL_FILENAME)
        with open("./data/guild.txt", "r") as file:
            for line in file:
                line = line.strip()
                self.__guild_list.update({line: 0})
        u.log_info("Количество членов гильдии: {}".format(len(self.__guild_list)))

    def __init__(self, bot):
        self.__bot = bot
        self.fill_guildlist()
        self.__init_roles()
        self.__init_time_roles()

    def __save_timed_roles(self):
        with open("./data/timeroles.json", "w") as file:
            tr_json = jsonpickle.encode(self.timed_roles, unpicklable=True)
            file.write(tr_json)

    def __init_time_roles(self):
        if os.path.exists("./data/timeroles.json"):
            with open("./data/timeroles.json", "r") as file:
                s = file.read()
                if len(s) < 1:
                    return
                self.timed_roles = jsonpickle.decode(s)

    def __init_roles(self):
        role_init = 0b00000
        for dcGuild in self.__bot.guilds:
            for r in dcGuild.roles:
                match r.name:
                    case c.ADMIN_ROLE:
                        self.dc_roles.admin_role_id = r.id
                        role_init = role_init | 0b00001
                    case c.PLAYER_ROLE:
                        self.dc_roles.player_role_id = r.id
                        role_init = role_init | 0b00010
                    case c.UNCONFIRM_ROLE:
                        self.dc_roles.unconfirmed_role_id = r.id
                        role_init = role_init | 0b00100
                    case c.CHILL_ROLE:
                        self.dc_roles.chill_role_id = r.id
                        role_init = role_init | 0b01000
                    case c.BOT_ROLE:
                        self.dc_roles.bot_role_id = r.id
                        role_init = role_init | 0b10000
        #   читаем и заполняем нужные роли
        if role_init < 1:
            u.log_critical("Не найдены роли по их именам, проверьте файл constant.py")
            return False
        if role_init < 3:
            u.log_critical("Не найдена роль ADMIN_ROLE, проверьте файл constant.py")
            return False
        if role_init < 7:
            u.log_critical("Не найдена роль UNCONFIRM_ROLE, проверьте файл constant.py")
            return False
        if role_init < 15:
            u.log_critical("Не найдена роль CHILL_ROLE, проверьте файл constant.py")
            return False
        if role_init < 31:
            u.log_critical("Не найдена роль BOT_ROLE, проверьте файл constant.py")
            return False
        u.log_info("Role init completed")
        return True

    async def validate_member(self, member: discord.Member):
        # разбираем ник дискорда
        m = u.parse_name(member.display_name)
        # если бот - сразу выходим
        try:
            if not get(member.roles, id=self.dc_roles.bot_role_id) is None:
                result = f"Пользователь {member.display_name} - бот, проверки не требуются"
                u.log_info(result)
                return result
            # если роль "Участник" и корявый ник - выходим, ставим "Неподтверждённые"
            if not m["valid"] and not get(member.roles, id=self.dc_roles.player_role_id) is None:
                await member.add_roles(get(member.guild.roles, id=self.dc_roles.unconfirmed_role_id))
                result = f"Формат имени пользователя {member.display_name} некорректный, ошибка проверки!!"
                u.log_info(result)
                return result
            # если нет в списке гильдии - лишаем всех ролей, выходим
            if m["valid"] and m["ingameName"] not in self.__guild_list:
                await u.clear_roles(member)
                await member.add_roles(get(member.guild.roles, id=self.dc_roles.unconfirmed_role_id))
                result = f"Пользователь {member.display_name} лишен роли Участник, ибо отсутствует в списке гильдии"
                u.log_info(result)
                dm = await self.__bot.create_dm(member)
                await dm.send('Вас нет в списке гильдии, все имеющиеся роли очищены!')
                return result
            # проверяем наличие роли "Участник", автоматически всем выставляем неподтвержденные, выходим
            if get(member.roles, id=self.dc_roles.player_role_id) is None:
                await member.add_roles(get(member.guild.roles, id=self.dc_roles.unconfirmed_role_id))
                result = f"Пользователь {member.display_name} не имеет роли Участник, присвоена роль Неподтверждённые"
                u.log_info(result)
                return result
            # проверяем наличие в гильде, ставим роль "Участник", если оной нет
            if m["valid"] and m["ingameName"] in self.__guild_list \
                    and get(member.roles, id=self.dc_roles.player_role_id) is None:
                await member.add_roles(get(member.guild.roles, id=self.dc_roles.player_role_id))
                await member.remove_roles(get(member.guild.roles, id=self.dc_roles.unconfirmed_role_id))
                result = f"Пользователь {member.display_name} не имел роли Участник, исправлено"
                u.log_info(result)
                return result
            return "Все проверки проведены - ошибок нет"
        except Exception as e:
            return str(e)

    def testTR(self, tr: TimeRole, modify: bool) -> int:
        for i, x in enumerate(self.timed_roles):
            if x.userId == tr.userId and x.roleId == tr.roleId:
                if modify:
                    x.endDate = tr.endDate
                return i
        if modify:
            self.timed_roles.append(tr)
        return -1

    async def add_timed_role(self, member: discord.Member, role: discord.Role, ed: float):
        try:
            tr = TimeRole(member.id, role.id, ed, member.display_name)
            if self.testTR(tr, True) == -1:
                u.log_info(f"Временная роль добавлена пользователю {member.display_name}")
                code = 0
                msg = "Роль добавлена"
            else:
                code = 1
                msg = "Роль продлена"
            await member.add_roles(get(member.guild.roles, id=self.dc_roles.chill_role_id))
            self.__save_timed_roles()
            return code, msg
        except Exception as e:
            return -1, str(e)

    async def validate_timed_role(self, member: discord.Member, role: discord.Role):
        if not get(member.roles, id=self.dc_roles.bot_role_id) is None:
            u.log_info(f"Пользователь {member.display_name} бот, пропускаем")
            return True, "ALL OK"
        iTr = self.testTR(TimeRole(member.id, role.id, 0, member.display_name), False)
        # роль не является временной
        if iTr == -1:
            err = f"Не найдена временная роль {role.name} у пользователя {member.display_name}"
            return False, err
        # является, но нет у персонажа
        r = get(member.roles, id=role.id)
        if r is None:
            err = f"{role.name} отсутствует у пользователя {member.display_name}!"
            return False, err
        # всё есть, проверяем - жива или нет. Если просрочена - очищаем
        u.log_info(f"Пользователь {member.display_name}, найдена временная роль {r.name}, срок до {datetime.datetime.fromtimestamp(self.timed_roles[iTr].endDate)}")
        if self.timed_roles[iTr].endDate < time.time():
            await member.remove_roles(get(member.guild.roles, id=role.id))
            self.timed_roles.pop(iTr)
            self.__save_timed_roles()
            u.log_info(f"Временная роль очищена у пользователя {member.display_name}")
        return True, "ALL OK"

    async def remove_timed_role(self, member: discord.Member, role: discord.Role):
        # проверяем, что роль временная, живая и на персонаже
        result, err = await self.validate_timed_role(member, role)
        if not result:
            return True, err
        # чистим
        iTr = self.testTR(TimeRole(member.id, role.id, 0, member.display_name), False)
        await member.remove_roles(get(member.guild.roles, id=role.id))
        self.timed_roles.pop(iTr)
        self.__save_timed_roles()
        u.log_info(f"Временная роль очищена у пользователя {member.display_name}")
        return True, err

    async def check_guild(self):
        g: discord.Guild
        for g in self.__bot.guilds:
            t = time.time_ns()
            u.log_info(f"Старт цикла проверки сервера: {g.name}")
            m: discord.Member
            for m in g.members:
                if not get(m.roles, id=self.dc_roles.bot_role_id) is None:
                    continue
                u.log_info(f"Проверка мембера: {m.display_name}")
                r: discord.Role
                for r in m.roles:
                    await self.validate_timed_role(m, r)
            u.log_info(f"Цикл проверки сервера {g.name} закончен, затрачено {(time.time_ns() - t)/1000000} мс")
