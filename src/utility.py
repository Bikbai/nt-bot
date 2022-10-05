import datetime
import re
from json import JSONEncoder

from colorama import init, Back, Fore, Style
import discord.member
from discord.utils import get
from re import finditer

import guild


def log_info(string):
    print(Fore.GREEN + "[{}] [INFO    ] {}".format(
                         datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"), string))


def log_warning(string):
    print(Fore.BLUE + "[{}] [WARNING ] {}".format(
                         datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"), string))


def log_critical(string):
    print(Fore.RED + "[{}] [CRITICAL] {}".format(
                         datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"), string))


def parse_name(memberName):
    regex = r"^(?P<officier>\*?) *\[(?P<ticker>\S*)\] (?P<ingameName>\w*)\W*(?:\((?P<callname>.*)\))?$"
    matches = re.finditer(regex, memberName, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        x = match.groupdict()
        x["valid"] = True
        return x
    return {"valid": False}


async def clear_roles(member: discord.Member):
    for r in member.roles:
        if r.position != 0:
            log_info(f"Removing role {r.name}")
            await member.remove_roles(r)


def jsonKeys2int(x):
    if isinstance(x, dict):
            return {int(k):v for k,v in x.items()}
    return x


class EnhancedJSONEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def parce_datestr(dt_string: str):
    try:
        return {0: datetime.datetime.strptime(dt_string, "%d.%m.%y").timestamp()}
    except Exception as e:
        return {1: "Формат даты дд.мм.гг, например 01.01.23"}