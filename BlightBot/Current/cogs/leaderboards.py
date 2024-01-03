import discord
from discord.ext import commands
from discord import app_commands
from devLogging import devLogging
from hypixelAPI import hypixelAPI

class Leaderboards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener(name='on_ready')
    async def on_ready(self):
        await self.bot.tree.sync()
        devLogging.info(msg='Cog finished loading', module=__name__)




async def setup(bot):
    await bot.add_cog(Leaderboards(bot))
