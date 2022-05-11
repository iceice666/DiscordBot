import logging
import discord
from src import config
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


bot = discord.Bot(owner_ids=config.owner_ids)

bot.load_extension('src.functions')
bot.load_extension('src.functions.music')
bot.load_extension('src.listener')


logger = logging.getLogger("DiscordMusicBot")
logger.setLevel(logging.DEBUG)
logger_formatter = logging.Formatter(
    '[%(asctime)s][%(levelname)s][%(pathname)s][%(name)s]:\n%(message)s',
)

console = logging.StreamHandler()
console.setLevel(level=logging.INFO)
console.setFormatter(logger_formatter)
logger.addHandler(console)

file = logging.FileHandler(".log", encoding='utf-8', mode='w')
file.setLevel(level=logging.DEBUG)
file.setFormatter(logger_formatter)
logger.addHandler(file)


logger.info("Starting bot")


def run():
    bot.run(config.bot_token)
