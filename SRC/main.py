# bot.py
import time
from turtle import update
import discord
import urllib.request
import asyncio
import colorama
from colorama import init, Back, Fore, Style
from discord.ext import commands
from discord.utils import get
from asyncio import sleep
import datetime
import os.path

# как сохраняем
destination = 'guild.txt'
# ссылка на список
url = 'http://nordic-tribe.ru/guildlist.php'

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(intents=intents, command_prefix="rp$")

# список
GOOD_LIST = []

# это необходимо для отображения цветов в консоли
init()

#timers 0 - member, 1 - roleid, 2 - date
roleTimer = [ ]

ADMIN_ROLE = 844129239983718432
PLAYER_ROLE = 932867826589523998
UNCONFIRM_ROLE = 1008059672890191923

async def updateList():
    GOOD_LIST.clear()
    # заполняем наш массив списком с сайта
    urllib.request.urlretrieve(url, destination)
    with open("../guild.txt", "r") as file:
        for line in file:
            line = line.strip()
            GOOD_LIST.append(line)


async def updateTimeRoleList():
    roleTimer.clear()
    if os.path.exists("../timeroles.json"):
        with open("../timeroles.json", "r") as file:
            for line in file:
                line = line.split(' ')
                roleTimer.append([bot.guilds[0].get_member(int(line[0])),int(line[1]), line[2]])


async def timeRoleListToFile():
    with open("../timeroles.json", "w") as file:
        for timer in roleTimer:
            print(timer)
            file.write("{} {} {}".format(timer[0].id,timer[1],timer[2]))

async def checkMember(member, isCommand=False, ctx=None):
    print("Проверяю {} на сервере {}...".format(member.display_name, member.guild))
    dt = datetime.datetime.now()
    dt_string = dt.strftime("%d.%m.%Y %H:%M")
    if member.display_name[0] == '*':
        return
    if get(member.guild.roles, id=PLAYER_ROLE) not in member.roles:
        #print(Fore.RED + "[{}] Проверка окончена: {} ({}) - нету роли участник".format(dt_string, member,
        #                                                                               member.display_name))
        if isCommand:
            await ctx.reply("У {} нет роли участник".format(member))
        return
    nickname_array = member.display_name.split(' ')
    match len(nickname_array):
        case 1:
            if get(member.guild.roles, id=PLAYER_ROLE) in member.roles:
                await member.add_roles(get(member.guild.roles, id=UNCONFIRM_ROLE))
                print(Fore.RED + "[{}] Проверка окончена: {} ({}) - неправильный никнейм".format(dt_string, member,
                                                                                                 member.display_name))
                if isCommand:
                    await ctx.reply(
                        "Проверка окончена: {} ({}) - неправильный никнейм".format(member, member.display_name))
        case 2:
            if get(member.guild.roles, id=PLAYER_ROLE) in member.roles:
                if nickname_array[1] not in GOOD_LIST:
                    await member.add_roles(get(member.guild.roles, id=UNCONFIRM_ROLE))
                    print(Fore.RED + "[{}] Проверка окончена: {} ({}) - нету в списке".format(dt_string, member,
                                                                                              member.display_name))
                    if isCommand:
                        await ctx.reply(
                            "Проверка окончена: {} ({}) - нету в списке".format(member, member.display_name))
                else:
                    if get(member.guild.roles, id=UNCONFIRM_ROLE) in member.roles:
                        await member.remove_roles(get(member.guild.roles, id=UNCONFIRM_ROLE))
                    print(Fore.GREEN + "[{}] Проверка окончена: {} ({}) всё хорошо".format(dt_string, member,
                                                                                           member.display_name))
                    if isCommand:
                        await ctx.reply("Проверка окончена: {} ({}) всё хорошо".format(member, member.display_name))
        case 3:
            if get(member.guild.roles, id=PLAYER_ROLE) in member.roles:
                if nickname_array[1] not in GOOD_LIST:
                    await member.add_roles(get(member.guild.roles, id=UNCONFIRM_ROLE))
                    print(Fore.RED + "[{}] Проверка окончена: {} ({}) - нету в списке".format(dt_string, member,
                                                                                              member.display_name))
                    if isCommand:
                        await ctx.reply(
                            "Проверка окончена: {} ({}) - нету в списке".format(member, member.display_name))
                else:
                    if get(member.guild.roles, id=UNCONFIRM_ROLE) in member.roles:
                        await member.remove_roles(get(member.guild.roles, id=UNCONFIRM_ROLE))
                    print(Fore.GREEN + "[{}] Проверка окончена: {} ({}) всё хорошо".format(dt_string, member,
                                                                                           member.display_name))
                    if isCommand:
                        await ctx.reply("Проверка окончена: {} всё хорошо".format(member, member.display_name))
        case 4:
            if get(member.guild.roles, id=PLAYER_ROLE) in member.roles:
                if nickname_array[1] not in GOOD_LIST:
                    await member.add_roles(get(member.guild.roles, id=UNCONFIRM_ROLE))
                    print(Fore.RED + "[{}] Проверка окончена: {} ({}) - нету в списке".format(dt_string, member,
                                                                                              member.display_name))
                    if isCommand:
                        await ctx.reply(
                            "Проверка окончена: {} ({}) - нету в списке".format(member, member.display_name))
                else:
                    if get(member.guild.roles, id=UNCONFIRM_ROLE) in member.roles:
                        await member.remove_roles(get(member.guild.roles, id=UNCONFIRM_ROLE))
                    print(Fore.GREEN + "[{}] Проверка окончена: {} ({}) всё хорошо".format(dt_string, member,
                                                                                           member.display_name))
                    if isCommand:
                        await ctx.reply("Проверка окончена: {} ({}) всё хорошо".format(member, member.display_name))


async def checkGuild(guild, fromCommand=False, ctx=None):
    # Обновляем список
    await updateList()
    # Смотрим все сервера
    print("Запущена проверка..")
    print("Проверяю сервер {}".format(guild))
    for member in guild.members:
        await checkMember(member)
    if fromCommand:
        await ctx.reply("Проверка окончена.")


@bot.command()
async def check(ctx, memberID):
    if get(ctx.guild.roles, id=ADMIN_ROLE) not in ctx.author.roles:
        await ctx.reply("Недостаточно полномочий.")
    else:
        if ctx.guild.get_member(int(memberID)) is None:
            await ctx.reply("Неправильный ID или нет такого участника на сервере!")
            return
        await checkMember(ctx.guild.get_member(int(memberID)), True, ctx)


@bot.command()
async def startCheck(ctx):
    if get(ctx.guild.roles, id=ADMIN_ROLE) not in ctx.author.roles:
        await ctx.reply("Недостаточно полномочий.")
    else:
        await ctx.reply("Запустил проверку.")
        await checkGuild(ctx.guild, True, ctx)


@bot.command()
async def timerole(ctx, userid : int, roleid : int,date):
    if get(ctx.guild.roles, id=ADMIN_ROLE) not in ctx.author.roles:
        await ctx.reply("Недостаточно полномочий.")
    else:
        if get(ctx.guild.roles, id=roleid) not in ctx.guild.get_member(userid).roles:
            await ctx.guild.get_member(userid).add_roles(get(ctx.guild.roles, id=roleid))
            roleTimer.append([ctx.guild.get_member(userid),roleid,date])
            await timeRoleListToFile()
            await ctx.reply("Установил временную роль.")
        else:
            await ctx.reply("У участника уже есть данная роль.")
        await checkTimers()

@bot.command()
async def timeroleupdate(ctx, userid : int, roleid : int, newdate):
    if get(ctx.guild.roles, id=ADMIN_ROLE) not in ctx.author.roles:
        await ctx.reply("Недостаточно полномочий.")
    else:
        for timer in roleTimer:
            if timer[0].id == userid and timer[1] == roleid:
                timer[2] = newdate
                await timeRoleListToFile()
                await ctx.reply("Временная роль обновлена.")
                return

async def checkTimers():
    dt_str = datetime.datetime.now()
    for timer in roleTimer:
        if timer[2] == dt_str.strftime("%d.%m.%y"):
            await timer[0].remove_roles(get(timer[0].roles, id=timer[1]))
            print("Убрал роль {} у {}".format(get(timer[0].guild.roles, id=timer[1]).name,timer[0].display_name))
            roleTimer.remove(timer)
            await timeRoleListToFile()

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print("------")
    await updateTimeRoleList()
    while True:
        try:
            for guild in bot.guilds:
                await checkGuild(guild)
            await checkTimers()
        except Exception as e:
            print(e)
        await asyncio.sleep(3600)


bot.run('OTk5MjYwOTk3MTA3ODU5NTU2.GaT_Q9.hgcqiBvnSSIyru_TufIadXPtGMqVCf5EhxNFRE')