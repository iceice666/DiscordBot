
from .music import MusicCmd

import logging


def setup(bot):
    bot.add_cog(MusicCmd(bot))
    logging.getLogger('DiscordMusicBot').debug(
        "Registering MusicCmd successful")
