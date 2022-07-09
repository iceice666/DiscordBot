
import logging
import time
import uuid


import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands
from discord.utils import escape_markdown


from .player import _PLAYER
from ... import config



class quickplay(commands.Cog):

    def __init__(self):
        self.quickplay_list=[]
        self.on_edit=None

    qp=SlashCommandGroup("quickplay","快速播放")

    @qp.command(name="create")
    async def qp_create(self, ctx, name=uuid.uuid3(), current_queue=False):
        self.quickplay_list.append(self.qpInstance(name))
        await ctx.respond(f'Created quickplay list {name}')

    @qp.command(name="edit")
    async def qp_edit(self,ctx,name):
        if name is None:
            pass
        else:
            self.quickplay_list.append(self.on_edit)
            for i,e in enumerate(self.quickplay_list):
                if e.name==name:
                    self.on_edit=self.quickplay_list.pop(i)
                    await ctx.respond(f"edit mode")

    @qp.command(name="remove")
    async def qp_remove(self,ctx,name):
        for i,e in enumerate(self.quickplay_list):
            if e.name==name:
                self.quickplay_list.pop(i)

    edit=qp.create_subgroup("edit","編輯")
    @edit.command(name="add")
    async def edit_add(self,ctx):
        pass



