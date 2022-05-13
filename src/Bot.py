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
    '[%(asctime)s][%(levelname)s][%(name)s][%(module)s]\n%(message)s', datefmt="%Y-%m-%d %p %I:%M:%S"
)

console = logging.StreamHandler()
console.setLevel(level=logging.INFO)
console.setFormatter(logger_formatter)
logger.addHandler(console)

file = logging.FileHandler(".log", encoding='utf-8', mode='w')
file.setLevel(level=logging.DEBUG)
file.setFormatter(logger_formatter)
logger.addHandler(file)

bot = discord.Bot(owner_ids=config["BOT"]["owner_ids"])


def run():
    logger = logging.getLogger("DiscordMusicBot")
    for i in extension:
        bot.load_extension(i)
        logger.info(f'Extension {i} loaded', extra={'classname': __name__})

    logger.info("Starting bot", extra={'classname': __name__})
    bot.run(config["BOT"]["token"])
