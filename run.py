
from src.Bot import BOT
from src import config

for account in config["BOT"]["accounts"]:
    BOT(account).run()
