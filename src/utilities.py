import logging
import asyncio


class Log:
    def __init__(self):
        self.logger = logging.getLogger("DMB")

        self.logger.setLevel(level=logging.INFO)

        console = logging.StreamHandler()
        console.setLevel(level=logging.INFO)
        console_formatter = logging.Formatter(
            '[%(asctime)s][%(levelname)s][%(filename)s][%(module)s@line:%(lineno)d]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        console.setFormatter(console_formatter)

        self.logger.addHandler(console)

    @staticmethod
    def getLogger():
        return logging.getLogger("DMB")


async def log_and_respond(ctx, logger: logging.Logger,log_level:str, i18n, msg_id):
    '''
    `ctx` Discord ctx \n
    `logger` a Logger obj\n
    `log_level` the level of msg that will be send\n
    `i18n` i18n obj\n
    `msg_id` msg id\n
    '''

    getattr(logger,log_level)(getattr(i18n.CONSOLE, msg_id))
    await ctx.respond(getattr(i18n.TRANSLATION, msg_id))
