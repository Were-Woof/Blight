import discord
from discord.ext import commands
from discord import app_commands
from discord import ui
from hypixelAPI import hypixelAPI
from devLogging import devLogging
from databaseManager import databaseManager
from asyncio import sleep as asyncio_sleep

class Tickets(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):

        await self.bot.tree.sync()
        devLogging.info(msg='Cog finished loading', module=__name__)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.add_roles(self.bot.unverifiedRole, self.bot.guestRole, reason="Member joined")

    @app_commands.command(name="create-panel")
    async def create_panel(self, interaction: discord.Interaction, name: str, category: discord.CategoryChannel):
        await interaction.response.defer()
        await databaseManager.register_panel(interaction.guild.id, name, category.id)
        await interaction.followup.send("Panel registered", ephemeral=True)
        


async def setup(bot):
    await bot.add_cog(Tickets(bot))
