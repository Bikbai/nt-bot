import uuid
from enum import Enum
import datetime
from typing import Optional, List

import jsonpickle
import os
import time
import inspect as i

import discord.types.member
from attr import dataclass

import constant as c
from colorama import init, Back, Fore, Style
from discord.utils import get
from discord.ext import commands
import urllib.request
import utility as u
from constant import RolesEnum


class GuildMember:
    gMemberName = ""
    dcUserName = ""


class TimeRole:
    uid: uuid.uuid4()
    userId: int
    roleId: int
    endDate: float
    userName: Optional[str]
    nextRoleId: Optional[int]

    def __init__(self, ur, rl, ed, un=None, nr=None):
        self.uid = uuid.uuid4()
        self.userId = ur
        self.roleId = rl
        self.endDate = ed
        self.userName = un
        self.nextRoleId = nr


class TimeRoles:
    timed_roles: dict[str, TimeRole] = dict()

    def __init__(self):
        if os.path.exists(c.TR_FILENAME):
            with open(c.TR_FILENAME, "r") as file:
                s = file.read()
                if len(s) < 1:
                    return
                self.timed_roles = jsonpickle.decode(s)

    def find_1(self, owner: discord.Member, trId: int):
        for val in self.timed_roles.values():
            if val.userId == owner.id and val.roleId == trId:
                return val
        return None

    def find_2(self, owner: discord.Member, role: discord.Role):
        return self.find_1(owner, role.id)

    def save(self):
        with open(c.TR_FILENAME, "w") as file:
            jsonpickle.set_preferred_backend('json')
            jsonpickle.set_encoder_options('json', ensure_ascii=False)
            tr_json = jsonpickle.encode(self.timed_roles, unpicklable=True, indent=4)
            file.write(tr_json)

    def isTimedRole(self, owner: discord.Member, role: discord.Role) -> bool:
        iTr = self.testTR(TimeRole(owner.id, role.id, 0, owner.display_name, None), False)
        if iTr is None:
            return True
        return False

    def testTR(self, tr: TimeRole, modify: bool) -> Optional[TimeRole]:
        for key, val in self.timed_roles.items():
            if val.uid == tr.userId and val.roleId == tr.roleId:
                # нашлося
                if modify:
                    self.timed_roles[str(val.uid)].endDate = tr.endDate
                return val
        if modify:
            # не нашлося
            self.timed_roles[str(tr.uid)] = tr
            self.save()
        return None

    def removeByTimeRole(self, tr: TimeRole):
        try:
            self.timed_roles.pop(str(tr.uid))
        except Exception as e:
            u.log_critical(f"removeByTimeRole: {e}")
        self.save()

class GGuild:
    __guild_list = dict()
    bot: commands.Bot = commands.Bot
    trStorage: TimeRoles
    dc_roles: dict[str, discord.Role] = dict()
    rights: dict[str, List[discord.Role]] = dict()

    def check_rights(self, member: discord.Member) -> bool:
        command = i.stack()[1][3]
        if command is None:
            u.log_critical(f"Ошибка, проверка полномочий пустой команды, вызов из {u.get_stack()}")
            return False
        roles = self.rights.get(command)
        # для команды не назначены права
        if roles is None:
            return False
        # пересечение ролей и полномочий пустое
        if len(list(set(roles) & set(member.roles))) == 0:
            return False
        return True

    def fill_guildlist(self):
        self.__guild_list.clear()
        u.log_info('Читаем список мемберов с сайта гильдии')
        urllib.request.urlretrieve(c.GUILD_LIST_URL, c.GL_FILENAME)
        with open("./data/guild.txt", "r") as file:
            for line in file:
                line = line.strip().lower()
                self.__guild_list.update({line: 0})
        u.log_info("Количество членов гильдии: {}".format(len(self.__guild_list)))

    def __init_rights__(self):
        with open("./" + c.RIGHTS_FILENAME, "r") as file:
            s = file.read()
            rightList = jsonpickle.decode(s)
            g: discord.Guild
            for cmd in rightList:
                for roleName in rightList[cmd]:
                    for g in self.bot.guilds:
                        r: discord.Role
                        for r in g.roles:
                            if r.name == roleName:
                                if self.rights.get(cmd) is None:
                                    self.rights.update({cmd: list({r})})
                                else:
                                    self.rights[str(cmd)].append(r)
            return

    def __init__(self, bot):
        self.bot = bot
        self.trStorage = TimeRoles()
        self.fill_guildlist()
        self.__init_roles()
        self.__init_rights__()

    def __init_roles(self):
        for a in RolesEnum:
            dcGuild: discord.Guild
            for dcGuild in self.bot.guilds:
                role = discord.utils.get(dcGuild.roles, name=a.value)
                if role is None:
                    err = f"Сервер: {dcGuild.name}, не найдена роль {a.value}"
                    u.log_critical(err)
                    raise Exception(err)
                self.dc_roles[str(a.name)] = role
        return True

    async def validate_member(self, member: discord.Member, writeMode : bool = False):
        # разбираем ник дискорда
        m = u.parse_name(member.display_name)
        # если бот - сразу выходим
        try:
            if self.isBot(member):
                result = f"Пользователь {member.display_name} - бот, проверки не требуются"
                u.log_info(result)
                return result
            if not self.isPlayer(member):
                result = f"Пользователь {member.display_name} - не участник, проверки не требуются"
                u.log_info(result)
                return result
            # если роль "Участник" и корявый ник - выходим, ставим "Неподтверждённые"
            if self.isPlayer(member) and not m["valid"]:
                if writeMode:
                    await member.add_roles(get(member.guild.roles, id=self.dc_roles['UNCONFIRM_ROLE'].id))
                result = f"Формат имени пользователя {member.display_name} некорректный, выставлена роль Неподтверждённые!"
                u.log_info(result)
                return result
            # если нет в списке гильдии - выходим, ставим "Неподтверждённые"
            if self.isPlayer(member) and m["valid"] and m["ingameName"] not in self.__guild_list:
                result = f"Пользователь {member.display_name} не найден в гильдии, выставлена роль Неподтверждённые"
                if writeMode:
                    await member.add_roles(get(member.guild.roles, id=self.dc_roles['UNCONFIRM_ROLE'].id))
                u.log_info(result)
                return result
            return f"{member.display_name}: все проверки проведены - ошибок нет"
        except Exception as e:
            return str(e)

    async def add_timed_role(self, member: discord.Member, role: discord.Role, ed: float,
                             nextRole: Optional[discord.Role]):
        try:
            if nextRole is None:
                nextRoleId = None
            else:
                nextRoleId = nextRole.id
            tr = TimeRole(member.id, role.id, ed, member.display_name, nextRoleId)
            if self.trStorage.testTR(tr, True) == -1:
                u.log_info(f"Временная роль добавлена пользователю {member.display_name}")
                code = 0
                msg = "Роль добавлена"
            else:
                code = 1
                msg = "Роль продлена"
            await member.add_roles(get(member.guild.roles, id=role.id))
            return code, msg
        except Exception as e:
            return -1, str(e)

    async def __validate_timed_role__(self,
                                      member: discord.Member,
                                      role: discord.Role,
                                      author: Optional[discord.Member] = None):
        interactive: bool = False
        dm: discord.client.DMChannel
        if author:
            interactive = True
        if role is None:
            msg = f"__validate_timed_role__: Ошибка! Передана пустая роль туда, куда не следует!!!"
            u.log_critical(msg)
            if interactive: await self.dm(author, msg)
            return
        iTr = self.trStorage.find_2(member, role)
        if iTr is None:
            return
        # всё есть, проверяем - жива или нет. Если просрочена - очищаем
        msg = f"Мембер {member.display_name}, найдена временная роль {role.name}, срок до {datetime.datetime.fromtimestamp(iTr.endDate)}"
        u.log_info(msg)
        if interactive: await self.dm(author, msg)
        if iTr.endDate < time.time():
            await member.remove_roles(get(member.guild.roles, id=role.id))
            self.trStorage.removeByTimeRole(iTr)
            # если выставлена подменяющая роль - выставляем
            if iTr.nextRoleId is None:
                pass
            else:
                await member.add_roles(get(member.guild.roles, id=iTr.nextRoleId))
                u.log_info(f"Добавлена роль {get(member.guild.roles, id=iTr.nextRoleId).name}")
            msg = f"Временная роль очищена у пользователя {member.display_name}"
            u.log_info(msg)
            if interactive: await self.dm(author, msg)
        return

    async def validate_timed_role(self,
                                  member: discord.Member,
                                  role: Optional[discord.Role] = None,
                                  author: Optional[discord.Member] = None):
        interactive: bool = False
        if author:
            interactive = True
        if self.isBot(member):
            msg = f"Пользователь {member.display_name} бот, пропускаем"
            u.log_info(msg)
            if interactive: await self.dm(author, msg)
            return True, "ALL OK"
        if role is None:
            # проверяем все роли персонажа
            if interactive: await self.dm(author, "Роль не указана, проверяем все доступные роли мембера")
            for r in member.roles:
                await self.__validate_timed_role__(member, r, author)
        else:
            if not self.trStorage.isTimedRole(member, role) and interactive:
                await self.dm(author, "Указанная роль не является временной.")
                return False, "ALL OK"
            await self.__validate_timed_role__(member, role, author)
        return True, "ALL OK"

    async def remove_timed_role(self, member: discord.Member, role: discord.Role):
        # проверяем, что роль временная, живая и на персонаже
        result, err = await self.validate_timed_role(member, role)
        if not result:
            return True, err
        # чистим
        iTr = self.trStorage.testTR(TimeRole(member.id, role.id, 0, member.display_name), False)
        await member.remove_roles(get(member.guild.roles, id=role.id))
        self.trStorage.removeByTimeRole(iTr)
        u.log_info(f"Временная роль очищена у пользователя {member.display_name}")
        return True, err

    async def check_guild(self):
        g: discord.Guild
        for g in self.bot.guilds:
            t = time.time_ns()
            u.log_info(f"Старт цикла проверки сервера: {g.name}")
            m: discord.Member
            for m in g.members:
                if self.isBot(m):
                    continue
                u.log_info(f"Проверка мембера: {m.display_name}")
                await self.validate_member(m, True)
                await self.validate_timed_role(m)
            u.log_info(f"Цикл проверки сервера {g.name} закончен, затрачено {(time.time_ns() - t) / 1000000} мс")

    def isOfficier(self, member: discord.Member) -> bool:
        pname = u.parse_name(member.display_name)
        if pname['valid'] and pname['officier'] == '*' and self.isPlayer(member):
            return True
        return False

    def isAdmin(self, member: discord.Member):
        if get(member.roles, id=self.dc_roles['PLAYER_ROLE'].id) is None:
            return False
        return True

    def isBot(self, member: discord.Member):
        if get(member.roles, id=self.dc_roles['BOT_ROLE'].id) is None:
            return False
        return True

    def isReqruiter(self, member: discord.Member):
        if get(member.roles, id=self.dc_roles['REQRUITER_ROLE'].id) is None:
            return False
        return True

    def isPlayer(self, member: discord.Member):
        if get(member.roles, id=self.dc_roles["PLAYER_ROLE"].id) is None:
            return False
        return True
    def isUnconfirmed(self, member: discord.Member):
        if get(member.roles, id=self.dc_roles["UNCONFIRM_ROLE"].id) is None:
            return False
        return True

    async def dm(self,to: discord.Member, msg: str):
        if to is None:
            raise Exception("Метод dm: пустой параметр 'to'")
        dm = await self.bot.create_dm(to)
        await dm.send(msg)
        return
