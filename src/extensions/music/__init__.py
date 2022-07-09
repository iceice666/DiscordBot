



from .src.dc_interface import MusicCmd


def setup(bot):
    bot.add_cog(MusicCmd(bot))

