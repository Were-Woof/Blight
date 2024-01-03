import discord
from discord.ext import commands
from discord import app_commands
from devLogging import devLogging
from databaseManager import databaseManager
import asyncio
from config import server_id
from asyncio import sleep as asyncio_sleep
from hypixelAPI import hypixelAPI
import nest_asyncio
nest_asyncio.apply()

def permission_check(self, interaction: discord.Interaction):
    for role in (self.bot.adminRole, self.bot.developerRole):
        if role in interaction.user.roles:
            return True
    
    return False

class Developer_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def permission_error_log(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f'{interaction.command.name} raised permission error in {interaction.channel.mention}', description=f'**Command Author:** {interaction.user.mention}', colour=discord.Colour.red())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)
        return
    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()
        devLogging.info(msg='Cog finished loading', module=__name__)


    @app_commands.command(name='setup', description='developer command to register the server')
    async def setup(self, interaction: discord.Interaction, guildname: str, staffrole: discord.Role, adminrole: discord.Role, guestrole: discord.Role, guildmemberrole: discord.Role, unverifiedrole: discord.Role, acceptedrole: discord.Role, mvprole: discord.Role, developerrole: discord.Role, logchannel: discord.TextChannel, messagelogchannel: discord.TextChannel, waitinglistchannel: discord.TextChannel, absencesubmissionschannel: discord.TextChannel, apikey: str):
        if 'developerRole' in dir(self.bot):
            if permission_check(self, interaction):
                await databaseManager.register_server(interaction.guild.id, guildname, staffrole.id, adminrole.id, guestrole.id, guildmemberrole.id, unverifiedrole.id, acceptedrole.id, mvprole.id, developerrole.id, logchannel.id, messagelogchannel.id, waitinglistchannel.id, absencesubmissionschannel.id, apikey)
                await interaction.response.send_message('Server registered', ephemeral=True)
                return
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(interaction)
            return
        await databaseManager.register_server(interaction.guild.id, guildname, staffrole.id, adminrole.id, guestrole.id, guildmemberrole.id, unverifiedrole.id, acceptedrole.id, mvprole.id, developerrole.id, logchannel.id, messagelogchannel.id, waitinglistchannel.id, absencesubmissionschannel.id, apikey)
        await interaction.response.send_message('Server registered', ephemeral=True)
        return

    @app_commands.command(name='set-admin-role', description='developer command to set admin role')
    async def set_admin_role(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.defer()
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(interaction)
            return
        await databaseManager.update_admin_role(role.id)
        self.bot.adminRole = role
        embed = discord.Embed(description=f'{interaction.command.name} command run in {interaction.channel.mention}', colour=discord.Colour.blue())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)
        return

    @app_commands.command(name='set-staff-role', description='developer command to set staff role')
    async def set_staff_role(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.defer()
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(interaction)
            return
        await databaseManager.update_staff_role(role.id)
        self.bot.staffRole = role
        embed = discord.Embed(description=f'{interaction.command.name} command run in {interaction.channel.mention}', colour=discord.Colour.blue())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)
        return

    @app_commands.command(name='set-developer-role', description='developer command to set developer role')
    async def set_developer_role(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.defer()
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(interaction)
            return
        await databaseManager.update_developer_role(role.id)
        self.bot.developerRole = role
        embed = discord.Embed(description=f'{interaction.command.name} command run in {interaction.channel.mention}', colour=discord.Colour.blue())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)
        return

    @app_commands.command(name='set-unverified-role', description='developer command to set unverified role')
    async def set_unverified_role(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.defer()
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(interaction)
            return
        await databaseManager.update_unverified_role(role.id)
        self.bot.unverifiedRole = role
        embed = discord.Embed(description=f'{interaction.command.name} command run in {interaction.channel.mention}', colour=discord.Colour.blue())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)
        return

    @app_commands.command(name='set-guild-role', description='developer command to set guild member role')
    async def set_guild_member_role(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.defer()
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(interaction)
            return
        await databaseManager.update_guildMember_role(role.id)
        self.bot.guildMemberRole = role
        embed = discord.Embed(description=f'{interaction.command.name} command run in {interaction.channel.mention}', colour=discord.Colour.blue())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)
        return

    @app_commands.command(name='set-mvp-role', description='developer command to set mvp role')
    async def set_mvp_role(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.defer()
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(interaction)
            return
        await databaseManager.update_mvp_role(role.id)
        self.bot.mvpRole = role
        embed = discord.Embed(description=f'{interaction.command.name} command run in {interaction.channel.mention}', colour=discord.Colour.blue())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)
        return

    @app_commands.command(name='set-guest-role', description='developer command to set guest role')
    async def set_guest_role(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.defer()
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(interaction)
            return
        await databaseManager.update_guest_role(role.id)
        embed = discord.Embed(description=f'{interaction.command.name} command run in {interaction.channel.mention}', colour=discord.Colour.blue())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)
        return

    @app_commands.command(name='set-accepted-role', description='developer command to set accepted role')
    async def set_accepted_role(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.defer()
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(interaction)
            return
        await databaseManager.update_accepted_role(role.id)
        embed = discord.Embed(description=f'{interaction.command.name} command run in {interaction.channel.mention}', colour=discord.Colour.blue())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)
        return

    @app_commands.command(name='set-logs-channel', description='developer command to set logs channel')
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer()
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(interaction)
            return
        await databaseManager.update_log_channel(channel.id)
        embed = discord.Embed(description=f'{interaction.command.name} command run in {interaction.channel.mention}', colour=discord.Colour.blue())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)
        return

    @app_commands.command(name='set-waitinglist-channel', description='developer command to set waitinglist channel')
    async def set_waitinglist_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer()
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(interaction)
            return
        await databaseManager.update_waitingList_channel(self.bot.dbSession, channel.id)
        embed = discord.Embed(description=f'{interaction.command.name} command run in {interaction.channel.mention}', colour=discord.Colour.blue())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)
        return

    @app_commands.command(name='set-api-key', description='set the bots hypixel api key')
    async def set_api_key(self, interaction: discord.Interaction, key: str):
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.response.send_message(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await interaction.delete_original_response()
            await self.permission_error_log(interaction)
            return
        await databaseManager.update_api_key(key)
        hypixelAPI.API_KEY = key
        embed = discord.Embed(description=f'{interaction.command.name} command run in {interaction.channel.mention}', colour=discord.Colour.blue())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)
        return



    @app_commands.command(name='lookup')
    async def lookup(self, interaction: discord.Interaction, discordid: str):
        await interaction.response.defer()
        member = await databaseManager.fetch_member(int(discordid))
        if member == None:
            embed = discord.Embed(description='No member found with that discordID', colour=discord.Colour.red())
            await interaction.followup.send(embed=embed)
            return
        embed = discord.Embed(title=f'Member found', description=f'**Username:** {member.username}\n**discordID:** {member.discordID}\n**UUID:** {member.uuid}', colour=discord.Colour.blue())
        await interaction.followup.send(embed=embed)
        embed = discord.Embed(description=f'{interaction.command.name} command run in {interaction.channel.mention}', colour=discord.Colour.blue())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)
        return

    @app_commands.command(name='ping')
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f':ping_pong: {self.bot.latency}ms')
    

async def setup(bot):
    await bot.add_cog(Developer_Commands(bot))
