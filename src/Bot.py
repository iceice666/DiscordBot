import logging

import discord

from src import config


extension = [
    'src.functions',
    'src.functions.music',
    'src.listener'
]

print("\n")
print("""



             @@@@      @@@@
            @@@@    @@@@@
           @@@@   @@@@       @@@@     @@@@      @@@@@@@@@@@%     @@@@@@@@@@@
          @@@@@@@@@         @@@@     @@@@     @@@@                      @@@@
          @@@@@@@@@        @@@@      @@@      @@@@@@@@           @@@@@@@@@@
         @@@@  @@@@@       @@@      @@@@         @@@@@@@@     @@@@     @@@
        @@@@    @@@@@     @@@@     @@@@             @@@@    @@@@      @@@@
       @@@@      @@@@    @@@@@@@@@@@@@    @@@@@@@@@@@@@     @@@@@@@@@@@@@@



                     @@@@@@@@@@@@                          @@@@
                    @@@@     @@@@         @@@@             @@@
                   @@@@     @@@@      @@@@@@@@@@@     @@@@@@@@@@@@
                  @@@@@@@@@@@        @@@@      @@@@       @@@@
                 @@@@      @@@@    @@@@      @@@@       @@@@
                 @@@@      @@@@   @@@@      @@@@       @@@@
                @@@@    @@@@@@    @@@@    @@@@%        @@@@
               @@@@@@@@@@@         @@@@@@@@@           @@@@@@@@@


""")

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger_formatter = logging.Formatter(
    '[%(asctime)s][%(levelname)s][%(name)s][%(module)s]\n%(message)s\n', datefmt="%Y-%m-%d %p %I:%M:%S"
)

bot = discord.Bot(owner_ids=config["BOT"]["owner_ids"])

def run():
    global logger
    console = logging.StreamHandler()
    console.setLevel(level=logging.INFO)
    console.setFormatter(logger_formatter)
    logger.addHandler(console)

    logger = logging.getLogger("DiscordMusicBot")
    file = logging.FileHandler(".log", encoding='utf-8', mode='w')
    file.setLevel(level=logging.DEBUG)
    file.setFormatter(logger_formatter)
    logger.addHandler(file)

    logger = logging.getLogger("DiscordMusicBot")
    for i in extension:
        bot.load_extension(i)
        logger.info(f'Extension {i} loaded', extra={'classname': __name__})


    logger.info("Starting bot", extra={'classname': __name__})
    bot.run(config["BOT"]["token"])


def docker_run():
    global logger
    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(logger_formatter)
    logger.addHandler(console)

    logger = logging.getLogger("DiscordMusicBot")
    for i in extension:
        bot.load_extension(i)
        logger.info(f'Extension {i} loaded', extra={'classname': __name__})

    logger.info("Starting bot", extra={'classname': __name__})
    bot.run(config["BOT"]["token"])
