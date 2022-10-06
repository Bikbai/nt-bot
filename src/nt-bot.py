from version import show_version
import time
from datetime import datetime

import constant as c
import typing
import discord.member
import utility as u
from discord.ext import commands
from colorama import init
import asyncio
import guild as g

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

show_version()
u.log_info(f"Starting using token: {c.BOT_TOKEN}")

bot = commands.Bot(intents=intents, command_prefix="$")

init()

gld: g.GGuild
tread_count = 0


@bot.command(pass_context=True)
async def chill(ctx: commands.Context, subcommand: str, member: discord.Member, role: typing.Optional[discord.Role],
                ed: typing.Optional[str]):
    result = True
    err = 'OK'
    code = 0  # ok

    if subcommand != 'v' and ed is None:
        result = False
        err = 'Некорректный формат команды. $chill a|r|v @member @role DD.MM.YY'
    elif subcommand != 'v':
        if role is None:
            await ctx.author.send(f'Команда chill {subcommand} {member.display_name}: ОШИБКА. не указана роль')
            return
        r = u.parce_datestr(ed)
        if r.get(0) is None:
            await ctx.author.send(f'Команда chill {subcommand} {member.display_name} {role.name} {ed}: '
                                  f'ОШИБКА: {r.get(1)}')
            return
        if r.get(0) < time.time():
            await ctx.author.send(f'Команда chill {subcommand} {member.display_name} {role.name}: '
                                  f'ОШИБКА. Указана дата в прошлом')
            return
    if result:
        match subcommand:
            case 'a':
                code, err = await gld.add_timed_role(member, role, r.get(0))
            case 'r':
                code, err = await gld.remove_timed_role(member, role, r.get(0))
            case 'v':
                code, err = await gld.validate_timed_role(member, role)
            case _:
                code = False
                err = 'Некорректный формат команды. $chill a|r|v @member @role DD.MM.YY'
    if result or code != -1:
        await ctx.author.send(f'{member.display_name}: OK. {err}')
        return
    else:
        await ctx.author.send(f'{member.display_name}: ОШИБКА. {err}')


@bot.command(pass_context=True)
async def dm(ctx: commands.Context):
    await gld.check_guild()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        u.log_info(error)
        await ctx.author.send(f'ОШИБКА. Не указан параметр "{error.param.name}"')
    await ctx.author.send(f'Произошла ошибка {error}')


@bot.event
async def on_ready():
    global tread_count
    tread_count = tread_count + 1
    global gld
    gld = g.GGuild(bot)
    u.log_info(f"Logged in as {bot.user.name}, thread {tread_count}")

    while True:
        u.log_info(f'Запуск потока проверки, thread: {tread_count}')
        await gld.check_guild()
        u.log_info(f"Следующая проверка в: {datetime.fromtimestamp(time.time()+ c.SLEEP_DELAY)}")
        await asyncio.sleep(c.SLEEP_DELAY)


@bot.event
async def on_member_join(member):
    u.log_info("Member join event: {}".format(member.display_name))
    await gld.validate_member(member)

try:
    bot.run(c.BOT_TOKEN)
except Exception as e:
    u.log_critical(str(e))




