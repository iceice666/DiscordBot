
from .music import MusicCmd

import logging


def setup(bot):
    bot.add_cog(MusicCmd(bot))

