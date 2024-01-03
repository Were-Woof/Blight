import discord
from discord.ext import commands
from discord import app_commands
from databaseManager import databaseManager
from devLogging import devLogging
import time
from asyncio import sleep as asyncio_sleep
from config import server_id
import nest_asyncio
nest_asyncio.apply()
from hypixelAPI import hypixelAPI

class Role_Syncing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()
        devLogging.info(msg='Cog finished loading', module=__name__)

    @app_commands.command(name="sync")
    async def sync(self, interaction: discord.Interaction):
        await interaction.response.defer()
  
        guild_members = await hypixelAPI.get_guild_members(await databaseManager.fetch_guild_name())
        member_info = await databaseManager.fetch_member(interaction.user.id)
        
        if member_info == None:
            response = await interaction.followup.send("Couldn't find any information about you in the database, please verify to gain access to this command. If you think this is a mistake, please contact server staff", ephemeral=True)
            await asyncio_sleep(5)
            await response.delete()
            return
        
        member_uuid = member_info.uuid

        await interaction.user.remove_roles(self.bot.unverifiedRole, reason="Sync Command")
        for member in guild_members:
            if member['uuid'] == member_uuid:
                if member['rank'] == 'MVP':
                    await interaction.user.add_roles(self.bot.mvpRole, reason="Sync Command")
                await interaction.user.add_roles(self.bot.guildMemberRole, reason="Sync Command")
                await interaction.user.remove_roles(self.bot.guestRole, self.bot.acceptedRole, reason="Sync Command")
                break
        else:
            await interaction.user.add_roles(self.bot.guestRole, reason="Sync Command")
            await interaction.user.remove_roles(self.bot.mvpRole, reason="Sync Command")
            await interaction.user.remove_roles(self.bot.guildMemberRole, reason="Sync Command")
        response = await interaction.followup.send("Your roles have been updated", ephemeral=True)
        await asyncio_sleep(3)
        await response.delete()
        



    def get_delay(self, seconds=0, minutes=15, hours=0, days=0):
        return seconds + (minutes*60) + (hours*3600) + (days*86400)

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.syncing != False:
            return
        await self.sync_roles()

    
    
    async def sync_roles(self):
        self.bot.syncing = True
        try:
            members = await databaseManager.fetch_all_members()
            guildName = await databaseManager.fetch_guild_name()
            guild_members = await hypixelAPI.get_guild_members(guildName)
            member_list = []
            raw_member_list = []
            for member in guild_members:
                await asyncio_sleep(0.1)
                member_list.append(member['uuid'])

            for member in guild_members:
                await asyncio_sleep(0.1)
                raw_member_list.append(member)

            for member in members:
                await asyncio_sleep(1)
                devLogging.info(msg=f'Syncing member: {member.discordID}', module=__name__)
                checked_username = await hypixelAPI.get_username_from_uuid(member.uuid)
                if checked_username != member.username:
                    await databaseManager.update_member_username(member, checked_username)

                discord_member = discord.utils.get(self.bot.blight.members, id=member.discordID)
                
                if discord_member == None:
                    devLogging.warning(msg=f'No discord member found for user: {member.discordID}', module=__name__)
                    continue

                if member.uuid in member_list:
                    devLogging.info(f'Member {member.discordID} showed as in guild', module=__name__)
                    await asyncio_sleep(0.25)
                    for memb in raw_member_list:
                        if memb['uuid'] == member.uuid:
                            devLogging.info(msg=f'UUID match found for member: {member.discordID}', module=__name__)
                            await discord_member.add_roles(self.bot.guildMemberRole, reason="Blight Role Sync")
                            await discord_member.remove_roles(self.bot.guestRole, self.bot.acceptedRole, reason="Blight Role Sync")

                            if memb['rank'] == "MVP":
                                devLogging.info(msg=f'Confirmed member {member.discordID} as MVP', module=__name__)
                                await discord_member.add_roles(self.bot.mvpRole, reason="Blight Role Sync")
                            else:
                                await discord_member.remove_roles(self.bot.mvpRole, reason="Blight Role Sync")
                            break
                    else:
                        devLogging.warning(msg=f'Member {member.discordID} showed as in guild but cannot find uuid match')
                else:
                    await discord_member.add_roles(self.bot.guestRole, reason="Blight Role Sync")
                    await discord_member.remove_roles(self.bot.guildMemberRole, self.bot.mvpRole, reason="Blight Role Sync")
            else:
                self.bot.syncing = False
                devLogging.info('Role sync finished without breaking', module=__name__)
        except Exception as error:
            devLogging.error(msg=f'Role sync failed with error: {error}', module=__name__)
            await asyncio_sleep(5)
            self.bot.syncing = False


                

        
        
    async def old_sync_roles(self):
        self.bot.syncing = True
        try:
            devLogging.info("Starting member role sync", module=__name__)

            blight = self.bot.get_guild(server_id)
            await asyncio_sleep(1)
            await asyncio_sleep(1)

            guild_members = await hypixelAPI.get_guild_members(await databaseManager.fetch_guild_name())
            await asyncio_sleep(1)
            member_list = []
            for member in guild_members:
                await asyncio_sleep(0.1)
                member_list.append(member['uuid'])
            


            for member in blight.members:
                await asyncio_sleep(1)
                member_info = await databaseManager.fetch_member(member.id)
                if member_info == None:
                    devLogging.info(msg=f'Skipping unregistered member: {member.id}', module=__name__)
                    continue
                
                if member_info.uuid in member_list:
                    await asyncio_sleep(0.25)
                    devLogging.info(msg=f'Found member {member.id} in guild', module=__name__)
                    for i in guild_members:
                        if member_info.uuid == i['uuid']:
                            devLogging.info(msg=f'UUID match found for member: {member.id}', module=__name__)
                            await member.add_roles(self.bot.guildMemberRole, reason="Blight Role Sync")
                            await member.remove_roles(self.bot.guestRole, self.bot.acceptedRole, reason="Blight Role Sync")

                            if guild_members[i]["rank"] == "MVP":
                                devLogging.info(msg=f'Confirmed member {member.id} as MVP', module=__name__)
                                await member.add_roles(self.bot.mvpRole, reason="Blight Role Sync")

                            break
                else:
                    await member.add_roles(self.bot.guestRole, reason="Blight Role Sync")
                    await member.remove_roles(self.bot.guildMemberRole, reason="Blight Role Sync")
            else:
                self.bot.syncing = False
                print('Role sync finished without breaking')
        except Exception as error:
            for i in error:
                print(i)
                print(error)
                print('ROLE SYNC ERROR')
            await asyncio_sleep(5)
            self.bot.syncing = False
                

async def setup(bot):
    await bot.add_cog(Role_Syncing(bot))
