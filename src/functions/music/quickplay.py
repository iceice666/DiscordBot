
import logging
import time


import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands
from discord.utils import escape_markdown


from .player import _PLAYER
from ... import config



class quickplay(commands.Cog):

    def __init__(self):
        self.quickplay_list=[]

    qp=SlashCommandGroup("quickplay","快速播放")

    @qp.command(name="create")
    async def qp_create(self,ctx,name):
        self.quickplay_list.append(self.qpInstance(name))

    @qp.command(name="edit")
    async def qp_edit(self,ctx):
        pass

    edit=qp.create_subgroup("edit","編輯")
    @edit.command(name="add")
    async def edit_add(self,ctx):
        pass

    class qpInstance:
        def __init__(self,name):
            self.name=name
            self.playlist=[]
        def add(self,value):
            self.playlist.append(value)
