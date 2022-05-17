import logging

import discord

from src import config
import os


class BOT:

    def __init__(self, account) -> None:
        self.account = account


        extension: list
        with open(f"{os.getcwd()}/activate", mode="r") as f:
            extension = f.readlines()

        extension.append('src.listener')
        extension.append('src.functions')

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger_formatter = logging.Formatter(
        '\n[%(asctime)s][%(levelname)s][%(name)s][%(module)s]\n%(message)s', datefmt="%Y-%m-%d %p %I:%M:%S"
        )

        #console = logging.StreamHandler()
        #console.setLevel(level=logging.INFO)
        #console.setFormatter(logger_formatter)
        #logger.addHandler(console)

        logger = logging.getLogger("DiscordBot")
        file = logging.FileHandler(f"log/{account['client_id']}.log", encoding='utf-8', mode='w')
        file.setLevel(level=logging.DEBUG)
        file.setFormatter(logger_formatter)
        logger.addHandler(file)

        logger = logging.getLogger("DiscordBot")
        logger.info(f"""
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
               @@@@@@@@@@@         @@@@@@@@@           @@@@@@@@@""")


        self.bot = discord.Bot(owner_ids=config["BOT"]["owner_ids"])

        logger.info("Starting bot", extra={'classname': __name__})

        for i in extension:
            i = i.replace('\n', '')
            if i.startswith('#') or i == '':
                continue

            self.bot.load_extension(i)
            logger.info(f'Extension {i} loaded', extra={'classname': __name__})



    def run(self):

        self.bot.run(self.account['token'])
