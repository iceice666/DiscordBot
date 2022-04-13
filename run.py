

from MusicBot.Bot import BOT
from pprint import pprint


from disnake.ext.commands.errors import CommandInvokeError


need_continue = True

while need_continue:
    try:

        token=None
        with open("TOKEN", "r", encoding="utf-8") as f:
            token = f.read()

        bot = BOT(token)
        bot.setup()
        bot.run()

    except CommandInvokeError as e:

        if e.message == "disnake.ext.commands.errors.CommandInvokeError: Command raised an exception: ShutdownSignal:":
            pass
        elif e.message == "ShutdownSignal":
            need_continue = False

        bot.stop()
        bot.teardown()

    else:
        pprint(e)


print("DONE")
