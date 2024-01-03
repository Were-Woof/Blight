import discord
from discord.ext import commands
from discord import app_commands
from discord import ui
from hypixelAPI import hypixelAPI
from devLogging import devLogging
from databaseManager import databaseManager
from asyncio import sleep as asyncio_sleep
from config import developer_ids
from config import verify_msg
import nest_asyncio
nest_asyncio.apply()

class VerifyButtons(discord.ui.Button):
    def __init__(self, button: list):
        super().__init__(label=button[0], custom_id=button[1], style=button[2])


    async def callback(self, interaction: discord.Interaction):
        if self.custom_id == "verify":
            devLogging.event(msg='Button pressed with custom_id: verify', module=__name__)
            await interaction.response.send_modal(VerifyModal())
        
        
        if self.custom_id == "unverify":

            devLogging.event(msg='Button pressed with custom_id: unverify', module=__name__)
            await interaction.response.defer()
            embed = discord.Embed(description="Finding your data", colour=discord.Colour.blue())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            user = await databaseManager.fetch_member(interaction.user.id)
            if user == None:
                embed = discord.Embed(description="We didn't find any of your data in the database, if you think this is a mistake, please contact server staff", colour=discord.Colour.red())
                await response.edit(embed=embed)
                await asyncio_sleep(5)
                await response.delete()
                return
            
            embed = discord.Embed(description="Deleting your data from database", colour=discord.Colour.blue())
            await response.edit(embed=embed)
            await databaseManager.delete_member(interaction.user.id)
            embed = discord.Embed(description="Successfully deleted your data, updating your roles", colour=discord.Colour.green())
            await response.edit(embed=embed)

            unverifiedRole_id = await databaseManager.fetch_unverified_role()
            guildMemberRole_id = await databaseManager.fetch_guildMember_role()
            blight = interaction.guild
            unverifiedRole = discord.utils.get(blight.roles, id=unverifiedRole_id)
            guildMemberRole = discord.utils.get(blight.roles, id=guildMemberRole_id)
            await interaction.user.add_roles(unverifiedRole, reason="User unverified")
            await interaction.user.remove_roles(guildMemberRole, reason="User unverified")
            await asyncio_sleep(5)
            await response.delete()



class VerifyModal(ui.Modal, title='Verify'):
    username = ui.TextInput(label='Please enter your minecraft username', required=True, style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):

        devLogging.event(msg=f'Verification submission recieved with username: {self.username.value}', module=__name__)
        await interaction.response.defer()
        embed = discord.Embed(description="Verifying your username..", colour=discord.Colour.blue())
        response = await interaction.followup.send(embed=embed, ephemeral=True)
        session = await databaseManager.connect()
        user = await databaseManager.fetch_member(interaction.user.id)



        discord_query = await hypixelAPI.get_all_player_info_from_username(self.username.value)

        if discord_query['success'] == False:
            print(discord_query)
            embed = discord.Embed(description=f'Unable to find player: {self.username.value}\nPlease try again in a few minutes and check for any typo\'s\nIf this issue persists please contact a staff member', colour=discord.Colour.red())
            await interaction.followup.send(embed=embed)
            return

        elif discord_query['discord'].lower() == interaction.user.name:
            confirmed_name = await hypixelAPI.confirm_name(discord_query['discord'])

            guild_members = await hypixelAPI.get_guild_members(await databaseManager.fetch_guild_name())
            guestRole = interaction.guild.get_role(await databaseManager.fetch_guest_role())

            if user != None:

                if user.discordID == interaction.user.id:
                    await databaseManager.update_member_username(user, confirmed_name)
                    await databaseManager.update_member_uuid(user, discord_query['uuid'])
                    embed = discord.Embed(description="Your details have been updated", colour=discord.Colour.green())
                    await response.edit(embed=embed)
                    await asyncio_sleep(5)
                    await response.delete()
                    return
                
                await databaseManager.delete_member(user.discordID)
                await databaseManager.register_member(interaction.user.id, user.uuid, confirmed_name)
                await interaction.user.remove_roles(interaction.guild.get_role(await databaseManager.fetch_unverified_role()), reason="Server Verification")
                
                for member in guild_members:
                    await asyncio_sleep()
                    if member['uuid'] == discord_query['uuid']:
                        guildMemberRole = interaction.guild.get_role(await databaseManager.fetch_guildMember_role())
                        await asyncio_sleep(0.25)
                        if member['rank'] == 'MVP':
                            mvpRole = interaction.guild.get_role(await databaseManager.fetch_mvp_role())
                            await interaction.user.add_roles(mvpRole, reason="Server Verification")
                        await interaction.user.add_roles(guildMemberRole, reason="Server Verification")
                        await interaction.user.remove_roles(guestRole, reason="Server Verification")
                        break
                else:
                    await interaction.user.add_roles(guestRole, reason="Server Verification")
                await interaction.user.edit(confirmed_name)
                embed = discord.Embed(description="Your details have been updated", colour=discord.Colour.green())
                await response.edit(embed=embed)
                await asyncio_sleep(5)
                await response.delete()

            await databaseManager.register_member(interaction.user.id, discord_query['uuid'], confirmed_name)
            await interaction.user.remove_roles(interaction.guild.get_role(await databaseManager.fetch_unverified_role()), reason="Server Verification")

            guild_members = await hypixelAPI.get_guild_members(await databaseManager.fetch_guild_name())
            guestRole = interaction.guild.get_role(await databaseManager.fetch_guest_role())
            
            for member in guild_members:
                if member['uuid'] == discord_query['uuid']:
                    guildMemberRole = interaction.guild.get_role(await databaseManager.fetch_guildMember_role())
                    if member['rank'] == 'MVP':
                        mvpRole = interaction.guild.get_role(await databaseManager.fetch_mvp_role())
                        await interaction.user.add_roles(mvpRole, reason="Server Verification")
                    await interaction.user.add_roles(guildMemberRole, reason="Server Verification")
                    await interaction.user.remove_roles(guestRole, reason="Server Verification")
                    break
            else:
                await interaction.user.add_roles(guestRole, reason="Server Verification")

            await interaction.user.edit(nick=confirmed_name)
            embed = discord.Embed(description="Finished!", colour=discord.Colour.green())
            await response.edit(embed=embed)
            await asyncio_sleep(5)
            await response.delete()


        else:
            embed = discord.Embed(description="Verification Failed! Your discord account does not matched this username's linked account", colour=discord.Colour.red())
            await response.edit(embed=embed)
            await asyncio_sleep(5)
            await response.delete()
            return
        
        member_info = await databaseManager.fetch_member(interaction.user.id)
        checked_username = await hypixelAPI.get_username_from_uuid(member_info.uuid)
        if checked_username != member_info.username:
            await databaseManager.update_member_username(checked_username)

        return


def permission_check(self, interaction: discord.Interaction):
    for role in (self.bot.staffRole, self.bot.adminRole, self.bot.developerRole):
        if role in interaction.user.roles:
            return True
    
    return False

class Verification(commands.Cog):

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

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.add_roles(self.bot.unverifiedRole, self.bot.guestRole, reason="Member joined")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await databaseManager.delete_member(member.id)

    @app_commands.command(name='send-verify-message', description='verify your minecraft username')
    async def send_verify_msg(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            return
        embed = discord.Embed(title="Welcome to Blight", description=verify_msg, colour=discord.Colour.blue())
        embed.set_image(url='https://imgur.com/8ILZ3LX.gif')
        await interaction.channel.send(embed=embed, view=self.bot.VerifyView)
        response = await interaction.followup.send("Verify button sent", ephemeral=True)
        await asyncio_sleep(3)
        await response.delete()
        embed = discord.Embed(description=f'{interaction.command.name} command run in {interaction.channel.mention}', colour=discord.Colour.blue())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Verification(bot))
