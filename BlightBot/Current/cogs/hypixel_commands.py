import discord
from discord.ext import commands
from discord import app_commands
from devLogging import devLogging
from hypixelAPI import hypixelAPI
from databaseManager import databaseManager

def permission_check(self, interaction: discord.Interaction):
    for role in (self.bot.staffRole, self.bot.adminRole, self.bot.developerRole):
        if role in interaction.user.roles:
            return True
    
    return False

def legacy_permission_check(self, ctx):
    for role in (self.bot.staffRole, self.bot.adminRole, self.bot.developerRole):
        if role in ctx.author.roles:
            return True
    
    return False

class HypixelCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener(name='on_ready')
    async def on_ready(self):
        await self.bot.tree.sync()
        devLogging.info(msg='Cog finished loading', module=__name__)

    async def permission_error_log(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f'{interaction.command.name} raised permission error in {interaction.channel.mention}', description=f'**Command Author:** {interaction.user.mention}', colour=discord.Colour.red())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)
        return

    async def legacy_permission_error_log(self, ctx):
        embed = discord.Embed(title=f'{interaction.command.name} raised permission error in {ctx.channel.mention}', description=f'**Command Author:** {ctx.author.mention}', colour=discord.Colour.red())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.logChannel.send(embed=embed)
        return



    @app_commands.command(name='get-guild-bedwars-leaderboard')
    async def get_guild_bedwars_leaderboard(self, interaction: discord.Interaction, guild_name: str=''):
        await interaction.response.defer()
        if permission_check(self, interaction) == False and (interaction.user.id != 685116886215688192):
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(interaction)
            return
        embed = discord.Embed(description='Finding stats..', colour=discord.Colour.blue())
        r = await interaction.followup.send(embed=embed)
        
        if guild_name == '':
            guild_name = await databaseManager.fetch_guild_name()
        
        guild_members = await hypixelAPI.get_guild_members(guild_name)
        guild_members_with_stats = {}
        guild_members_index = {}
        num = 0
        for member in guild_members:
            num += 1
            username = await hypixelAPI.get_username_from_uuid(member['uuid'])
            stats = await hypixelAPI.get_bedwars_stats(member['uuid'])
            guild_members_with_stats[username] = stats
            guild_members_index[username] = stats['bw_index']
            embed = discord.Embed(description=f'Finding stats {num}/{len(guild_members)}', colour=discord.Colour.blue())
            await r.edit(embed=embed)
        

        embed = discord.Embed(description='Sorting results..', colour=discord.Colour.blue())
        await r.edit(embed=embed)

        lines = 0
        total_lines = 0
        msg = ''
        messages = []
        selected_player = None

        embed = discord.Embed(title=f'Bedwars Leaderboard for {guild_name}', colour=discord.Colour.green())
        await interaction.channel.send(embed=embed)

        while total_lines < len(guild_members_with_stats):
            if selected_player in guild_members_index:
                guild_members_index.pop(selected_player)
            if total_lines >= 40:
                
                if lines >= 40:
                    messages.append(msg)
                    embed = discord.Embed(description=msg, colour=discord.Colour.green())
                    await interaction.channel.send(embed=embed)
                    msg = ''
                    lines = 0
            
            elif lines >= 40:
                messages.append(msg)
                embed = discord.Embed(description=msg, colour=discord.Colour.green())
                await interaction.channel.send(embed=embed)
                msg = ''
                lines = 0


            highest_player_index = max(guild_members_index.values())

            for member in guild_members_index:
                if guild_members_index[member] == highest_player_index:
                    selected_player = member
                    msg = msg + f'\n**#{total_lines+1}:** ``{member}`` {guild_members_with_stats[member]["bw_stars"]}**★** FKDR: **{format(round(guild_members_with_stats[member]["bw_fkdr"], 2), ",")}** Index: **{format(int(guild_members_with_stats[member]["bw_index"]), ",")}**'
                    lines += 1
                    total_lines += 1
                    break


        messages.append(msg)
        embed = discord.Embed(description=msg, colour=discord.Colour.green())
        await interaction.channel.send(embed=embed)

        await r.delete()




    @app_commands.command(name='gap')
    async def gap(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(interaction)
            return
        embed = discord.Embed(description='Working..', colour=discord.Colour.blue())
        r = await interaction.followup.send(embed=embed)
        monitoredGuilds = await databaseManager.fetch_monitoredGuilds()
        guilds = monitoredGuilds.split(', ')
        guilds_gexp = {}
        blight_exp = await hypixelAPI.get_guild_gexp('Blight')
        for guild in guilds:
            guilds_gexp[guild] = await hypixelAPI.get_guild_gexp(guild) - blight_exp

        above = '## Guilds above Blight'
        below = '## Guilds below Blight'
        while len(guilds_gexp) > 0:
            max_value = max(guilds_gexp.values())
            for g in guilds_gexp:
                if guilds_gexp[g] == max_value:
                    if max_value >= 0:
                        above = above + f'\n**{g}:** {format(max_value, ",")}'
                    else:
                        below = below + f'\n**{g}:** {format(max_value, ",")}'
                    guilds_gexp.pop(g)
                    break
            

        embed = discord.Embed(title='Monitored Guilds Gexp Gap', description=f'{above}\n{below}', colour=discord.Colour.green())
        await r.edit(embed=embed)

    @app_commands.command(name='fetch-monitored-guilds')
    async def fetch_monitored_guilds(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(interaction)
            return
        guilds = await databaseManager.fetch_monitoredGuilds()
        await interaction.followup.send(guilds)
        
    
    @app_commands.command(name='add-monitored-guild')
    async def add_monitored_guild(self, interaction: discord.Interaction, guild: str):
        await interaction.response.defer()
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(interaction)
            return
        await databaseManager.add_monitoredGuild(guild)
        guilds = await databaseManager.fetch_monitoredGuilds()
        await interaction.followup.send(guilds)

    @app_commands.command(name='remove-monitored-guild')
    async def remove_monitored_guild(self, interaction: discord.Interaction, guild: str):
        await interaction.response.defer()
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(interaction)
            return
        await databaseManager.remove_monitoredGuild(guild)
        guilds = await databaseManager.fetch_monitoredGuilds()
        await interaction.followup.send(guilds)


    @app_commands.command(name='set-monitored-guilds')
    async def set_monitored_guilds(self, interaction: discord.Interaction, guilds: str):
        await interaction.response.defer()
        if permission_check(self, interaction) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(interaction)
            return
        await databaseManager.set_monitoredGuilds(guilds)
        await interaction.followup.send(guilds)

    @commands.command(name='gap')
    async def legacy_gap(self, ctx, *, ignored_stuff='None'):
        if legacy_permission_check(self, ctx) == False:
            embed = discord.Embed(description="You do not have permission to run this command", colour=discord.Colour.red())
            response = await ctx.send(embed=embed, ephemeral=True)
            await asyncio_sleep(3)
            await response.delete()
            await self.permission_error_log(ctx)
            return
        embed = discord.Embed(description='Working..', colour=discord.Colour.blue())
        r = await ctx.send(embed=embed)
        monitoredGuilds = await databaseManager.fetch_monitoredGuilds()
        guilds = monitoredGuilds.split(', ')
        guilds_gexp = {}
        blight_exp = await hypixelAPI.get_guild_gexp('Blight')
        for guild in guilds:
            guilds_gexp[guild] = await hypixelAPI.get_guild_gexp(guild) - blight_exp

        above = '## Guilds above Blight'
        below = '## Guilds below Blight'
        while len(guilds_gexp) > 0:
            max_value = max(guilds_gexp.values())
            for g in guilds_gexp:
                if guilds_gexp[g] == max_value:
                    if max_value >= 0:
                        above = above + f'\n**{g}:** {format(max_value, ",")}'
                    else:
                        below = below + f'\n**{g}:** {format(max_value, ",")}'
                    guilds_gexp.pop(g)
                    break
            

        embed = discord.Embed(title='Monitored Guilds Gexp Gap', description=f'{above}\n{below}', colour=discord.Colour.green())
        await r.edit(embed=embed)
        

            
        

        



async def setup(bot):
    await bot.add_cog(HypixelCommands(bot))
