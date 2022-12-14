from discord.utils import get
#from version import show_version
import time
from datetime import datetime
import inspect as i

import constant as c
import typing
import discord.member
import utility as u
from discord.ext import commands
from colorama import init
import asyncio
import guild as g
from src.client import MyClient
from src.gui import DropdownView, Feedback
from discord import app_commands

init()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = MyClient(intents=intents)

#show_version()
u.log_info(f"Starting using token: {c.BOT_TOKEN}")

gld: g.GGuild(client=client)
tread_count = 0


@client.tree.command()
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')


@client.tree.command()
async def test(interaction: discord.Interaction):
    await interaction.response.send_modal(Feedback())


@client.tree.command()
async def uclear(interaction: discord.Interaction):
    if not gld.check_rights(interaction.user):
        await interaction.response.send_message(f'У вас нет доступа к этой команде')
        return
    for p in interaction.guild.members:
        if gld.isUnconfirmed(p):
            await p.remove_roles(get(p.guild.roles, id=gld.dc_roles['UNCONFIRM_ROLE'].id))
            u.log_info(f"Очищен участник: {p.display_name}")
            await asyncio.sleep(5)


@client.tree.command()
async def newbie(interaction: discord.Interaction, member: discord.Member):
    if not gld.check_rights(interaction.user):
        await interaction.response.author.send(f'У вас нет доступа к этой команде')
        return
    if not gld.isPlayer(member):
        await interaction.response.author.send(f"Указанный персонаж должен иметь роль 'Участник'")
        return
    if gld.isOfficier(member):
        await interaction.response.author.send(f"Офицеру, серьезно?!")
        return
    endDate = time.time() + 30 * 24 * 3600
    await gld.add_timed_role(member, gld.dc_roles["NEWBIE_ROLE"], endDate, gld.dc_roles["TRIAL_ROLE"])
    await interaction.response.author.send(
        f'Мемберу {member.display_name} добавлена роль {gld.dc_roles["NEWBIE_ROLE"].name} сроком до {datetime.fromtimestamp(endDate)}')


@client.tree.command()
async def timerole(ctx: commands.Context, subcommand: str, member: discord.Member, role: typing.Optional[discord.Role],
                   ed: typing.Optional[str]):
    if not gld.check_rights(ctx.author):
        await ctx.author.send(f'У вас нет доступа к этой команде')
        return
    result = True
    err = 'OK'
    code = 0  # ok
    print(i.stack()[0][3])
    if subcommand != 'v' and ed is None:
        result = False
        err = 'Некорректный формат команды. rp$timerole a|r|v @member @role DD.MM.YY'
    elif subcommand != 'v':
        if role is None:
            await ctx.author.send(f'Команда rp$timerole {subcommand} {member.display_name}: ОШИБКА. не указана роль')
            return
        r = u.parce_datestr(ed)
        if r.get(0) is None:
            await ctx.author.send(f'Команда rp$timerole {subcommand} {member.display_name} {role.name} {ed}: '
                                  f'ОШИБКА: {r.get(1)}')
            return
        if r.get(0) < time.time():
            await ctx.author.send(f'Команда rp$timerole {subcommand} {member.display_name} {role.name}: '
                                  f'ОШИБКА. Указана дата в прошлом')
            return
    if result:
        match subcommand:
            case 'a':
                code, err = await gld.add_timed_role(member, role, r.get(0))
            case 'r':
                code, err = await gld.remove_timed_role(member, role, r.get(0))
            case 'v':
                code, err = await gld.validate_timed_role(member=member, role=None, author=ctx.author)
            case _:
                code = False
                err = 'Некорректный формат команды. $chill a|r|v @member @role DD.MM.YY'
    if result or code != -1:
        await ctx.author.send(f'{member.display_name}: OK. {err}')
        return
    else:
        await ctx.author.send(f'{member.display_name}: ОШИБКА. {err}')
    return



# команда проверки персонажей, или всей гильды
@client.tree.command()
async def check(ctx: commands.Context, mode: str = 'v', member: typing.Optional[discord.Member] = None):
    gld.fill_guildlist()
    writeMode = False
    if mode == 'w':
        writeMode = True
    if not gld.check_rights(ctx.author):
        await ctx.author.send(f'У вас нет доступа к этой команде')
        return
    if member is None:
        if writeMode:
            await ctx.author.send(f'Запущена проверка по всем членам гильдии в режиме исправления')
        else:
            await ctx.author.send(f'Запущена проверка по всем членам гильдии в режиме проверки')
        for m in ctx.guild.members:
            r = None
            r = await gld.validate_member(m, writeMode)
            if not r is None:
                pass
#                await ctx.author.send(r)
    else:
        if writeMode:
            await ctx.author.send(f'Проверяем и исправляем мембера: {member.display_name}')
        else:
            await ctx.author.send(f'Проверяем мембера: {member.display_name}')
        r = None
        r = await gld.validate_member(member, writeMode)
        if not r is None:
            await ctx.author.send(r)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        u.log_info(error)
        await ctx.author.send(f'ОШИБКА. Не указан параметр "{error.param.name}"')
    await ctx.author.send(f'Произошла ошибка: {error}')
    return


@client.event
async def on_ready():
    global gld
    gld = g.GGuild(client=client)
    u.log_info(f"Logged in as {client.user.display_name}")

    while True:
        u.log_info(f'Запуск проверки')
        await gld.check_guild()
        u.log_info(f"Следующая проверка в: {datetime.fromtimestamp(time.time() + c.SLEEP_DELAY)}")
        await asyncio.sleep(c.SLEEP_DELAY)



@client.event
async def on_member_join(member):
    u.log_info("Member join event: {}".format(member.display_name))
    await gld.validate_member(member)


try:
    client.run(c.BOT_TOKEN)
except Exception as e:
    u.log_critical(str(e))
