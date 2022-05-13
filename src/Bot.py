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

logger = logging.getLogger("DiscordMusicBot")
logger.setLevel(logging.DEBUG)
logger_formatter = logging.Formatter(
    '[%(asctime)s][%(levelname)s][%(name)s]:\n%(message)s', datefmt="%Y-%m-%d %p %I:%M:%S"
)

console = logging.StreamHandler()
console.setLevel(level=logging.DEBUG)
console.setFormatter(logger_formatter)
logger.addHandler(console)

file = logging.FileHandler(".log", encoding='utf-8', mode='w')
file.setLevel(level=logging.INFO)
file.setFormatter(logger_formatter)
logger.addHandler(file)

bot = discord.Bot(owner_ids=config["BOT"]["owner_ids"])


def run():
    for i in extension:
        bot.load_extension(i)
        logger.info(f'Extension {i} loaded')

    logger.info("Starting bot")
    bot.run(config["BOT"]["token"])
