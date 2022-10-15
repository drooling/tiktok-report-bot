import argparse
import contextlib
import ctypes
import json as jsonlib
import random
import urllib.parse
from os import system

import httpx
import trio
from colorama import Fore, init

init(autoreset=True)

REASONS = [int(line) for line in open("./reasons.txt", "r").readlines()]


def random_reason(base: str) -> str:
    pieces = urllib.parse.urlparse(base)
    qs = dict(urllib.parse.parse_qsl(pieces.query))
    qs.update({"reason": random.choice(REASONS)})
    return pieces._replace(query=urllib.parse.urlencode(qs)).geturl()


async def handle_response(resp: httpx.Response):
    with contextlib.suppress(Exception):
        json = jsonlib.loads(resp.text)
        if "banned" in json["status_msg"]:
            print(f"{Fore.LIGHTWHITE_EX}{json['extra']['logid']} - {Fore.LIGHTGREEN_EX}{json['status_msg']}")
            ctypes.windll.user32.MessageBoxW(0, "User has been banned.", "Successfully Banned", 0x0 | 0x30)
            exit(0)
        else:
            print(f"{Fore.LIGHTWHITE_EX}{json['extra']['logid']} - {Fore.LIGHTRED_EX}{json['status_msg']}")


async def report(client: httpx.AsyncClient, args, task_status=trio.TASK_STATUS_IGNORED):
    while 1:
        with contextlib.suppress(Exception):
            resp = await client.post(str(random_reason(args.url) if args.rotate else args.url))
            await handle_response(resp)


async def initialise():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("-r", dest="rotate", action="store_true")
    args = parser.parse_args()

    ctypes.windll.kernel32.SetConsoleTitleW(" - [ Surtains Report Bot - @surtains ] - ")
    system("clear")

    async with httpx.AsyncClient() as client:
        async with trio.open_nursery() as nursery:
            await nursery.start(report, client, args)


trio.run(initialise)
