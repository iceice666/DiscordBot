import logging

import discord

from src import config

if __name__ == '__main__':
    print('Use "python run.py" to run!')

extension = [
    'src.functions',
    'src.functions.music',
    'src.listener'
]


def load_extension():
    global bot
    for i in extension:
        bot.load_extension(i)
        logger.info(f'Extension {i} loaded', extra={'classname': __name__})


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




def _start():
    global logger
    logger = logging.getLogger("DiscordMusicBot")
    load_extension()

    bot = discord.Bot(owner_ids=config["BOT"]["owner_ids"])
    logger.info("Starting bot", extra={'classname': __name__})
    bot.run(config["BOT"]["token"])


def run():
    global logger
    console = logging.StreamHandler()
    console.setLevel(level=logging.INFO)
    console.setFormatter(logger_formatter)
    logger.addHandler(console)

    logger = logging.getLogger("DiscordMusicBot")
    file = logging.FileHandler("log/.log", encoding='utf-8', mode='w')
    file.setLevel(level=logging.DEBUG)
    file.setFormatter(logger_formatter)
    logger.addHandler(file)

    _start()


def docker_run():
    global logger
    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(logger_formatter)
    logger.addHandler(console)
    _start()
