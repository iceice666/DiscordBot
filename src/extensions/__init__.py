from .general import GeneralCmd, TestCmd

import logging


def setup(bot):
    bot.add_cog(GeneralCmd(bot))

    bot.add_cog(TestCmd(bot))
    
