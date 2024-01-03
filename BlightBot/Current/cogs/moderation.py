import discord
from discord.ext import commands
from discord import app_commands
from databaseManager import databaseManager
from devLogging import devLogging
from config import developer_ids
from asyncio import sleep as asyncio_sleep
from datetime import datetime, timedelta
from hypixelAPI import hypixelAPI
import nest_asyncio
nest_asyncio.apply()

def permission_check(self, interaction: discord.Interaction):
    for role in (self.bot.staffRole, self.bot.adminRole, self.bot.developerRole):
        if role in interaction.user.roles:
            return True
    
    return False

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()
        devLogging.info(msg='Cog finished loading', module=__name__)

    async def permission_error_log(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f'{interaction.command.name} raised permission error in {interaction.channel.mention}', description=f'**Command Author:** {interaction.user.mention}', colour=discord.Colour.red())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)
        return

    @app_commands.command(name='purge', description='deletes a set number of messages')
    async def purge(self, interaction: discord.Interaction, number: int):
        await interaction.response.defer()
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(interaction)
            return
        embed = discord.Embed(description=f'Deleting {number} messages..', colour=discord.Colour.green())
        msg = await interaction.followup.send(embed=embed)
        await asyncio_sleep(1)
        await msg.delete()
        await interaction.channel.purge(limit=number)
        embed = discord.Embed(title=f'{interaction.command.name} command run in {interaction.channel.mention}', description=f'**Messages deleted:** {number}', colour=discord.Colour.blue())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)
        return


    @app_commands.command(name='role', description='give or take a role from a member')
    async def role(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role, hidden: bool=False):
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.response.send_message(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(interaction)
            return
        if interaction.user.top_role.position <= role.position:
            embed = discord.Embed(description="You can only assign roles below your highest role", colour=discord.Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=hidden)
            await asyncio_sleep(3)
            await interaction.delete_original_response()
            await self.permission_error_log(interaction)
            return
        
        if role not in member.roles:
            try:
                await member.add_roles(role, reason=f"Role command ordered by {interaction.user} for role {role} targetting member {member}")
                embed = discord.Embed(description=f"Given role {role.mention} to {member.mention}", colour=discord.Colour.green())
                await interaction.response.send_message(embed=embed, ephemeral=hidden, allowed_mentions=False)
            except discord.errors.Forbidden:
                embed = discord.Embed(description="I don't have permission to do this", colour=discord.Colour.red())
                await interaction.response.send_message(embed=embed, ephemeral=hidden)
                await asyncio_sleep(3)
                await interaction.delete_original_response()
                return
        else:
            try:
                await member.remove_roles(role, reason=f"Role command ordered by {interaction.user} for role {role} targetting member {member}")
                embed = discord.Embed(description=f"Removed role {role.mention} from {member.mention}", colour=discord.Colour.green())
                await interaction.response.send_message(embed=embed, ephemeral=hidden, allowed_mentions=False)
            except discord.errors.Forbidden:
                embed = discord.Embed(description="I don't have permission to do this", colour=discord.Colour.red())
                await interaction.response.send_message(embed=embed, ephemeral=hidden)
                await asyncio_sleep(3)
                await interaction.delete_original_response()
                return
        embed = discord.Embed(title=f'{interaction.command.name} command run in {interaction.channel.mention}', description=f'**Target User:** {member.mention}\n**Target Role:** {role.mention}', colour=discord.Colour.blue())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)
        return

    @app_commands.command(name='kick', description='kick a member from the server')
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str="None", hidden: bool=False):
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=hidden)
            await asyncio_sleep(3)
            await interaction.delete_original_response()
            await self.permission_error_log(interaction)
            return
        if interaction.user.top_role.position <= member.top_role.position:
            embed = discord.Embed(description="You can only kick members below your highest role", colour=discord.Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=hidden)
            await asyncio_sleep(3)
            await interaction.delete_original_response()
            await self.permission_error_log(interaction)
            return
        try:
            await member.kick(reason=f"Kick command ordered by {interaction.user} with reason: {reason}")
        except discord.errors.Forbidden:
            embed = discord.Embed(description="I don't have permission to do this", colour=discord.Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=hidden)
            await asyncio_sleep(3)
            await interaction.delete_original_response()
            return
        else:
            embed = discord.Embed(description=f"**Kicked member:** {member.mention}\n**Reason:** {reason}", colour=discord.Colour.green())
            await interaction.response.send_message(embed=embed, ephemeral=hidden)
        embed = discord.Embed(title=f'{interaction.command.name} command run in {interaction.channel.mention}', description=f'**Target User:** {member.mention}\n**Reason:** {reason}', colour=discord.Colour.blue())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)
        return


    @app_commands.command(name='ban', description='ban a member from the server')
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str="None", hidden: bool=False):
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=hidden)
            await asyncio_sleep(3)
            await interaction.delete_original_response()
            await self.permission_error_log(interaction)
            return
        if interaction.user.top_role.position <= member.top_role.position:
            embed = discord.Embed(description="You can only ban members below your highest role", colour=discord.Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=hidden)
            await asyncio_sleep(3)
            await interaction.delete_original_response()
            await self.permission_error_log(interaction)
            return
        try:
            await member.ban(reason=f"Ban command ordered by {interaction.user} with reason: {reason}")
        except discord.errors.Forbidden:
            embed = discord.Embed(description="I don't have permission to do this", colour=discord.Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=hidden)
            await asyncio_sleep(3)
            await interaction.delete_original_response()
            return
        else:
            embed = discord.Embed(description=f"**Banned member:** {member.mention}\n**Reason:** {reason}", colour=discord.Colour.green())
            await interaction.response.send_message(embed=embed, ephemeral=hidden)
        embed = discord.Embed(title=f'{interaction.command.name} command run in {interaction.channel.mention}', description=f'**Target User:** {member.mention}\n**Reason:** {reason}', colour=discord.Colour.blue())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)
        return


    @app_commands.command(name='mute', description='timeout a member for a set duration')
    async def mute(self, interaction: discord.Interaction, member: discord.Member, days: int=0, hours: int=0, minutes: int=0, reason: str="No reason given", hidden: bool=False):
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await interaction.delete_original_response()
            await self.permission_error_log(interaction)
            return
        if interaction.user.top_role.position <= member.top_role.position:
            embed = discord.Embed(description="You can only mute members below your highest role", colour=discord.Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=hidden)
            await asyncio_sleep(3)
            await interaction.delete_original_response()
            await self.permission_error_log(interaction)
            return

        if days + hours + minutes == 0:
            hours = 1
        try:
            await member.timeout(timedelta(days=days, hours=hours, minutes=minutes), reason=f"Mute command ordered by {interaction.user} with reason: {reason}")
        except discord.errors.Forbidden:
            embed = discord.Embed(description="I don't have permission to do this", colour=discord.Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=hidden)
        else:
            embed = discord.Embed(description=f"**Timed out member:** {member.mention}\n**Duration:** {days} day(s), {hours} hour(s) and {minutes} minute(s)\n**Reason:** {reason}", colour=discord.Colour.green())
            await interaction.response.send_message(embed=embed, ephemeral=hidden)
        embed = discord.Embed(title=f'{interaction.command.name} command run in {interaction.channel.mention}', description=f'**Target User:** {member.mention}\n**Reason:** {reason}\n**Duration:** {days} day(s), {hours} hour(s) and {minutes} minute(s)', colour=discord.Colour.blue())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)
        return


    @app_commands.command(name='forcelink', description='force link a member to a minecraft account')
    async def forcelink(self, interaction: discord.Interaction, member: discord.Member, username: str):
        await interaction.response.defer()
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            await interaction.followup.send(embed=embed, ephemeral=True)
            await self.permission_error_log(interaction)
            return
        uuid = await hypixelAPI.get_uuid(username)
        if uuid == False:
            embed = discord.Embed(description=f'Unable to find uuid for player with username: {username}', colour=discord.Colour.red())
            await interaction.followup.send(embed=embed)
            return
        username = await hypixelAPI.confirm_name(username)
        member_info = await databaseManager.fetch_member(member.id)
        if member_info != None:
            await databaseManager.delete_member(member.id)
        await databaseManager.register_member(member.id, uuid, username)
        try:
            await member.edit(nick=username)
        except:
            pass
        
        guild_members = await hypixelAPI.get_guild_members(await databaseManager.fetch_guild_name())
        await member.remove_roles(self.bot.unverifiedRole, reason="Forcelink command")
        for player in guild_members:
            if player['uuid'] == uuid:
                await member.add_roles(self.bot.guildMemberRole, reason="Forcelink Command")
                await member.remove_roles(self.bot.guestRole, reason="Forcelink Command")
                if player['rank'] == 'MVP':
                    await member.add_roles(self.bot.mvpRole, reason="Forcelink Command")
                break
        else:
            await member.add_roles(self.bot.guestRole, reason="Forcelink Command")
            await member.remove_roles(self.bot.mvpRole, reason="Forcelink Command")
            await member.remove_roles(self.bot.guildMemberRole, reason="Forcelink Command")
        embed = discord.Embed(description=f'## Member Registered\n**Member:** {member.mention}\n**Username:** {username}\n**UUID:** {uuid}\n\nPlease run ``/sync`` to sync your roles.', colour=discord.Colour.green())
        await interaction.followup.send(embed=embed)
        embed = discord.Embed(description=f'{interaction.command.name} command run in {interaction.channel.mention}', colour=discord.Colour.blue())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)
        return



    




async def setup(bot):
    await bot.add_cog(Moderation(bot))
