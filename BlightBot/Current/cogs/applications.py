import discord
from discord.ext import commands
from discord import app_commands
from devLogging import devLogging
from databaseManager import databaseManager
from asyncio import sleep as asyncio_sleep
from hypixelAPI import hypixelAPI
from config import reqs
from config import developer_ids
from config import app_message
import nest_asyncio
nest_asyncio.apply()

class ApplyButtons(discord.ui.Button):
    def __init__(self,button: list):
        super().__init__(label=button[0], custom_id=button[1], style=button[2])
        self.blocked_users = []



    async def callback(self, interaction: discord.Interaction):

        if self.custom_id == "guild_apply":
            devLogging.event(f'Guild apply button pressed by {interaction.user.id}', module=__name__)
            #
            #
            # The following code is run if the guild application button is pressed.
            #
            #
            if interaction.user.id in self.blocked_users:
                embed = discord.Embed(description="You cannot apply again yet", colour=discord.Colour.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
                await asyncio_sleep(5)
                await interaction.delete_original_response()
                await asyncio_sleep(10)
                if interaction.user.id in self.blocked_users:
                    self.blocked_users.remove(interaction.user.id)
                return
            
            self.blocked_users.append(interaction.user.id)
            await interaction.response.defer()
            user_info = await databaseManager.fetch_member(interaction.user.id)

            if user_info == None:
                embed = discord.Embed(description="You cannot apply until you have registered", colour=discord.Colour.red())
                response = await interaction.followup.send(embed=embed, ephemeral=True)
                self.blocked_users.remove(interaction.user.id)
                await asyncio_sleep(5)
                await response.delete()
                session.close()
                return

            current_apps = await databaseManager.fetch_guild_app_by_user(user_info.discordID)
            
            if current_apps != None:
                embed = discord.Embed(description="You cannot apply while you have an open application", colour=discord.Colour.red())
                response = await interaction.followup.send(embed=embed, ephemeral=True)
                self.blocked_users.remove(interaction.user.id)
                await asyncio_sleep(5)
                await response.delete()
                session.close()
                return
            
            bw_stats = await hypixelAPI.get_bedwars_stats(user_info.uuid)
            duels_stats = await hypixelAPI.get_duels_stats(user_info.uuid)

            stats = {}

            guild_data = await hypixelAPI.get_guild_from_uuid(user_info.uuid)
            
            for i in bw_stats:
                stats[i] = bw_stats[i]

            for i in duels_stats:
                stats[i] = duels_stats[i]

            meets_reqs = False

            for option in reqs:
                for stat in option:

                    if option[stat] > stats[stat]:
                        break
                else:
                    meets_reqs = True
                    break

            if meets_reqs == True:

                waitingListChannel_id = await databaseManager.fetch_waitingList_channel()
                acceptedRole_id = await databaseManager.fetch_accepted_role()
                waitingListChannel = discord.utils.get(interaction.guild.text_channels, id=waitingListChannel_id)
                acceptedRole = discord.utils.get(interaction.guild.roles, id=acceptedRole_id)
                embed = discord.Embed(description=f'**Congratulations, you\'ve been accepted into the guild! <@{interaction.user.id}> **\nPlease leave your current guild and make sure your guild privacy is set to none. Instructions in GIF above.\n> Minecraft username: **{user_info.username}**', colour=discord.Colour.green())
                await waitingListChannel.send(content=interaction.user.mention, embed=embed)
                await interaction.user.add_roles(acceptedRole)
                if interaction.user.id in self.blocked_users:
                    self.blocked_users.remove(interaction.user.id)
                session.close()
                return
            
            # Formating the stats for easy viewing in the application channel
            stats = {"Bedwars Stars": format(bw_stats["bw_stars"], ','),
                    "Bedwars FKDR": format(round(bw_stats["bw_fkdr"], 2), ','),
                    "Bedwars Index": format(int(bw_stats["bw_index"]), ','),
                    "Duels Wins": format(duels_stats["duels_wins"], ','),
                    "Duels WLR": format(round(duels_stats["duels_wlr"], 2), ',')
                    }
            
            staffRole_id = await databaseManager.fetch_staff_role()
            staffRole = discord.utils.get(interaction.guild.roles, id=staffRole_id)
            adminRole_id = await databaseManager.fetch_admin_role()
            adminRole = discord.utils.get(interaction.guild.roles, id=adminRole_id)
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
                staffRole: discord.PermissionOverwrite(read_messages=True, send_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True),
                adminRole: discord.PermissionOverwrite(read_messages=True, send_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)
            }
            application_channel = await interaction.guild.create_text_channel(f"Application-{user_info.username}", reason="Guild Application Created", overwrites=overwrites)
            msg = f"Discord: {interaction.user.mention}\nMinecraft username: {user_info.username}\n"
            for stat in stats:
                msg = msg + f"\n{stat}: **{stats[stat]}**"

            if guild_data != None:
                gexp = await hypixelAPI.get_member_gexp_from_guild_member_data(guild_data['members'], user_info.uuid)
                msg = msg + f"\n\nGuild: **{guild_data['name']}**\nWeekly Gexp: **{format(gexp, ',')}**"
            else:
                msg = msg + "\n\nThis player is not in a guild"
            

            embed = discord.Embed(title="Guild Application", description=msg, colour=discord.Colour.green())
            
            await application_channel.send(content=interaction.user.mention, embed=embed)
            await databaseManager.register_ticket(application_channel.id, interaction.guild.id, interaction.user.id, "Guild Applications")
            if interaction.user.id in self.blocked_users:
                self.blocked_users.remove(interaction.user.id)


def permission_check(self, interaction: discord.Interaction):
    for role in (self.bot.staffRole, self.bot.adminRole, self.bot.developerRole):
        if role in interaction.user.roles:
            return True
        
    return False

def legacy_permission_check(self, ctx: commands.Context):
    for role in (self.bot.staffRole, self.bot.adminRole, self.bot.developerRole):
        if role in ctx.author.roles:
            return True
        
    return False


class Applications(commands.Cog):
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

    async def legacy_permission_error_log(self, ctx: commands.Context):
        embed = discord.Embed(title=f'{ctx.command.name} raised permission error in {ctx.channel.mention}', description=f'**Command Author:** {ctx.author.mention}', colour=discord.Colour.red())
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        await self.bot.logChannel.send(embed=embed)


    @app_commands.command(name='send-apply-button', description='apply to join the guild')
    async def send_apply_msg(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(interaction)
            return
        
        embed = discord.Embed(description=app_message, colour=discord.Colour.blue())
        await interaction.channel.send(embed=embed, view=self.bot.ApplyView)
        response = await interaction.followup.send("Apply button sent", ephemeral=True)
        await asyncio_sleep(3)
        await response.delete()
        embed = discord.Embed(description=f'{interaction.command.name} command run in {interaction.channel.mention}', colour=discord.Colour.blue())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)


    @app_commands.command(name='accept', description='accept a guild application')
    async def accept(self, interaction: discord.Interaction, app_channel: discord.TextChannel=None):
        await interaction.response.defer()
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(interaction)
            return
        
        if app_channel == None:
            app_channel = interaction.channel
        application = await databaseManager.fetch_guild_app(app_channel.id, app_channel.guild.id)

        if application == None:
            response = await interaction.followup.send("That is not a valid application", ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            return
        
        member = discord.utils.get(app_channel.members, id=application.ownerID)
        member_info = await databaseManager.fetch_member(application.ownerID)
        guild_data = await hypixelAPI.get_guild_from_uuid(member_info.uuid)

        await member.add_roles(self.bot.acceptedRole, reason=f"Guild Application Accepted by: {interaction.user}")
        await databaseManager.delete_guild_app(app_channel.id, app_channel.guild.id)
        embed = discord.Embed(description=f'**Congratulations, you\'ve been accepted into the guild! <@{member_info.discordID}> **\nPlease leave your current guild and make sure your guild privacy is set to none. Instructions in GIF above.\n> Minecraft username: **{member_info.username}**', colour=discord.Colour.green())
        await self.bot.waitingListChannel.send(content=f'<@{member_info.discordID}>', embed=embed)
        await app_channel.send("Application accepted! Channel will be deleted in 30 seconds")
        await interaction.followup.send("Done", ephemeral=True)
        await asyncio_sleep(30)
        await app_channel.delete()


    @app_commands.command(name='deny', description='deny a guild application')
    async def deny(self, interaction: discord.Interaction, app_channel: discord.TextChannel=None):
        await interaction.response.defer()
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(interaction)
            return
        
        if app_channel == None:
            app_channel = interaction.channel
        application = await databaseManager.fetch_guild_app(app_channel.id, app_channel.guild.id)

        if application == None:
            response = await interaction.followup.send("That is not a valid application", ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            return
        
        member = discord.utils.get(app_channel.members, id=application.ownerID)
        await databaseManager.delete_guild_app(app_channel.id, app_channel.guild.id)
        await app_channel.send(f"{member.mention} your application has been denied, sorry. This channel will be deleted in 10 minutes.")
        await interaction.followup.send("Done", ephemeral=True)
        await asyncio_sleep(600)
        await app_channel.delete()

    
    
    
    
    
    
    
    @commands.command(name='accept')
    async def legacy_accept(self, ctx: commands.Context, app_channel: discord.TextChannel=None):
        if legacy_permission_check(self, ctx) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await ctx.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.legacy_permission_error_log(ctx)
            return
        
        if app_channel == None:
            app_channel = ctx.channel
        application = await databaseManager.fetch_guild_app(app_channel.id, app_channel.guild.id)

        if application == None:
            response = await ctx.send("That is not a valid application", ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            return
        
        
        member = discord.utils.get(app_channel.members, id=application.ownerID)
        member_info = await databaseManager.fetch_member(application.ownerID)
        guild_data = await hypixelAPI.get_guild_from_uuid(member_info.uuid)

        await member.add_roles(self.bot.acceptedRole, reason=f"Guild Application Accepted by: {ctx.author}")
        await databaseManager.delete_guild_app(app_channel.id, app_channel.guild.id)

        embed = discord.Embed(description=f'**Congratulations, you\'ve been accepted into the guild! <@{member_info.discordID}> **\nPlease leave your current guild and make sure your guild privacy is set to none. Instructions in GIF above.\n> Minecraft username: **{member_info.username}**', colour=discord.Colour.green())
        await self.bot.waitingListChannel.send(content=f'<@{member_info.discordID}>', embed=embed)
        await app_channel.send("Application accepted! Channel will be deleted in 30 seconds")
        await ctx.send("Done", ephemeral=True)
        await asyncio_sleep(30)
        await app_channel.delete()


    @commands.command(name='deny')
    async def legacy_deny(self, ctx: commands.Context, app_channel: discord.TextChannel=None):
        if legacy_permission_check(self, ctx) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await ctx.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.legacy_permission_error_log(ctx)
            return
        
        if app_channel == None:
            app_channel = ctx.channel
        application = await databaseManager.fetch_guild_app(app_channel.id, app_channel.guild.id)

        if application == None:
            response = await ctx.send("That is not a valid application", ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            return
        
        member = discord.utils.get(app_channel.members, id=application.ownerID)
        await databaseManager.delete_guild_app(app_channel.id, app_channel.guild.id)
        await app_channel.send(f"{member.mention} your application has been denied, sorry. This channel will be deleted in 10 minutes.")
        await ctx.send("Done", ephemeral=True)
        await asyncio_sleep(600)
        await app_channel.delete()




    @commands.command(name='accepted')
    async def legacy_accepted(self, ctx: commands.Context, member: discord.Member):
        rec_role = discord.utils.get(ctx.guild.roles, id=964508866891120652)
        if not any((rec_role in ctx.author.roles, legacy_permission_check(self, ctx))):
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await ctx.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.legacy_permission_error_log(ctx)
            return
        
        if self.bot.acceptedRole in member.roles:
            embed = discord.Embed(description=f'Removed {self.bot.acceptedRole.mention} from {member.mention}', colour=discord.Colour.green())
            await member.remove_roles(self.bot.acceptedRole, reason=f'Accepted command by {ctx.author}')
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description=f'Given {self.bot.acceptedRole.mention} to {member.mention}', colour=discord.Colour.green())
            await member.add_roles(self.bot.acceptedRole, reason=f'Accepted command by {ctx.author}')
            await ctx.send(embed=embed)



        
        



async def setup(bot):
    await bot.add_cog(Applications(bot))
