import discord
from discord.ext import commands
from discord import app_commands
from devLogging import devLogging
import nest_asyncio
nest_asyncio.apply()

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener(name='on_ready')
    async def on_ready(self):
        await self.bot.tree.sync()
        devLogging.info(msg='Cog finished loading', module=__name__)

    @commands.Cog.listener(name='on_message_delete')
    async def on_message_delete(self, message):
        if self.bot.user == message.author:
            return
        try:
            base_embed = discord.Embed(title=f'Message deleted in {message.channel.mention}', description=message.content, colour=discord.Colour.dark_red())
            base_embed.set_author(name=message.author, icon_url=message.author.avatar)
            embeds = [base_embed]
            for image in message.attachments:
                embed = discord.Embed(description='Attachment for deleted message')
                embed.set_image(url=image.url)
                embeds.append(embed)
            for embed_msg in message.embeds:
                embed = discord.Embed(description='Embed for deleted message')
                embed.add_field(name=embed_msg.title, value=embed_msg.description)
                embed.set_image(url=embed_msg.image.url)
                embeds.append(embed)
            
            await self.bot.messageLogChannel.send(embeds=embeds)
        except:
            pass

    @commands.Cog.listener(name='on_message_edit')
    async def on_message_edit(self, before, after):
        if self.bot.user == after.author:
            return
        if before.content == after.content:
            return
        embed = discord.Embed(title=f'Message edited at {after.jump_url}', description=f'## Before \n{before.content} \n## After \n{after.content}', colour=discord.Colour.orange())
        embed.set_author(name=after.author, icon_url=after.author.avatar)


        await self.bot.messageLogChannel.send(embed=embed)




async def setup(bot):
    await bot.add_cog(Logging(bot))
