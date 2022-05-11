from .general import GeneralCmd, TestCmd

import logging


def setup(bot):
    bot.add_cog(GeneralCmd(bot))
    logging.getLogger('DiscordMusicBot').debug(
        "Registering GeneralCmd successful")
    bot.add_cog(TestCmd(bot))
    logging.getLogger('DiscordMusicBot').debug(
        "Registering TestCmd successful")
