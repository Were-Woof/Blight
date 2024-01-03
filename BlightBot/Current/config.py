#
# The information stored here is all hardcoded and seperate from the database. Modifying the TOKEN or database details may prevent the bot from functioning. 
#

TOKEN = ''
GUILD_NAME = 'Blight'
server_id = 586693158751174667

database_password = ''
database_username = ''
database_name = ''
database_endpoint = ''
database_url = f'mysql+aiomysql://{database_username}:{database_password}@{database_endpoint}/{database_name}'

reqs = [{"bw_index": 2000}, {"bw_index": 1500, "duels_wins": 3000, "duels_wlr": 2}]

developer_ids = []

app_message = """
    Press the button below the begin the application process, we'll handle the rest. If you run into any issues please contact a staff member.
    """

verify_msg = """
    In order for us to know who you are on Hypixel, we require you to verify yourself before interacting with the discord.

    **To verify yourself:**
    > - Link your discord account to your Hypixel account. There is a tutorial gif after this message.
    > - After that, press the verify button below.
    > - Then type your minecraft username in the popup and press submit

    - If you find you are unable to verify yourself, please check if your Discord account is linked to your Minecraft account on Hypixel by following the instructions shown in the gif below.

    - If any problems arise after following these instructions and looking at the gif, or you don't have a Minecraft account, contact any online staff member by pinging them or DMing them to assist you.
"""
