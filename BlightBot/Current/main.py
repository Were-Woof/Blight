from gevent import monkey
monkey.patch_all()
import discord
from discord.ext import commands
from discord import app_commands
import os
from cogs.verification import VerifyButtons
from cogs.applications import ApplyButtons
from databaseManager import databaseManager
from devLogging import devLogging
from config import developer_ids, server_id
from asyncio import sleep as asyncio_sleep
import asyncio
import nest_asyncio
nest_asyncio.apply()


class BlightBot(commands.Bot):

    def __init__(self):

        intents = discord.Intents.all()
        super().__init__(command_prefix='b!', intents=intents)
        self.syncing = False

    async def load_cogs(self):
        # Finds all python files within the 'cogs' folder.
        # The bot will attempt to load all found python files as a cog.
        devLogging.info(msg='Finding cogs', module=__name__)
        for cog in os.listdir('./JackBlight/cogs'):
            if cog.endswith('.py'):
                devLogging.info(msg=f'Loading cog {cog}', module=__name__)
                await self.load_extension(f'cogs.{cog[:-3]}')
        devLogging.info(msg='Finished finding cogs', module=__name__)

    async def setup_hook(self) -> None:

        # Registering all past verification and application buttons.
        self.VerifyView = discord.ui.View(timeout=None)
        self.ApplyView = discord.ui.View(timeout=None)
        
        verify_buttons = [["Verify", "verify", discord.enums.ButtonStyle.green],
        ["Unverify", "unverify", discord.enums.ButtonStyle.red]]

        apply_buttons = [["Apply", "guild_apply", discord.enums.ButtonStyle.green]]

        for button in verify_buttons:
            self.VerifyView.add_item(VerifyButtons(button=button))

        for button in apply_buttons:
            self.ApplyView.add_item(ApplyButtons(button=button))

        self.add_view(self.VerifyView)
        self.add_view(self.ApplyView)

        # Loading cogs
        await self.load_cogs()


bot = BlightBot()

@bot.event
async def on_ready():
    devLogging.info(msg=f'Logged into bot account {bot.user}', module=__name__)

    bot.blight = bot.get_guild(server_id)
    
    # Loading roles and channels from the database. These roles and channels can be references in all of the bot's cogs as "self.bot.<role/channel attribute name>", example: self.bot.developerRole
    # Please note that these attributes are not available in buttons/modals as they do not have access to the bot class. These attributes are defined for the button upon each button being pressed within the buttons code.
    try:
        devLogging.info(msg="Loading unverified, guildMember, guest, staff and admin roles", module=__name__)
        staffRole_id = await databaseManager.fetch_staff_role()
        adminRole_id = await databaseManager.fetch_admin_role()
        guestRole_id = await databaseManager.fetch_guest_role()
        unverifiedRole_id = await databaseManager.fetch_unverified_role()
        guildMemberRole_id = await databaseManager.fetch_guildMember_role()
        mvpRole_id = await databaseManager.fetch_mvp_role()
        acceptedRole_id = await databaseManager.fetch_accepted_role()
        developerRole_id = await databaseManager.fetch_developer_role()
    except Exception as e:
        devLogging.error(msg="Ran into an issue loading roles from database", module=__name__)
        print(e)
    else:
        bot.unverifiedRole = discord.utils.get(bot.blight.roles, id=unverifiedRole_id)
        bot.guildMemberRole = discord.utils.get(bot.blight.roles, id=guildMemberRole_id)
        bot.staffRole = discord.utils.get(bot.blight.roles, id=staffRole_id)
        bot.adminRole = discord.utils.get(bot.blight.roles, id=adminRole_id)
        bot.guestRole = discord.utils.get(bot.blight.roles, id=guestRole_id)
        bot.mvpRole = discord.utils.get(bot.blight.roles, id=mvpRole_id)
        bot.acceptedRole = discord.utils.get(bot.blight.roles, id=acceptedRole_id)
        bot.developerRole = discord.utils.get(bot.blight.roles, id=developerRole_id)
        devLogging.info(msg="Finished loaded unverified, guildMember, guest, staff and admin roles", module=__name__)
    
    try:
        devLogging.info(msg="Loading channels", module=__name__)
        waitingListChannel_id = await databaseManager.fetch_waitingList_channel()
        logChannel_id = await databaseManager.fetch_log_channel()
        messageLogChannel_id = await databaseManager.fetch_messageLog_channel()
    except Exception as e:
        devLogging.error(msg="Ran into an issue loading roles from database", module=__name__)
        print(e)
    else:
        bot.waitingListChannel = discord.utils.get(bot.blight.text_channels, id=waitingListChannel_id)
        bot.logChannel = discord.utils.get(bot.blight.text_channels, id=logChannel_id)
        bot.messageLogChannel = discord.utils.get(bot.blight.text_channels, id=messageLogChannel_id)
        devLogging.info(msg='Finished loading channels', module=__name__)

from config import TOKEN
bot.run(TOKEN)
