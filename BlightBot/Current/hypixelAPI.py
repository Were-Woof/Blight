import grequests
from databaseManager import databaseManager
import asyncio
import aiohttp
import nest_asyncio
nest_asyncio.apply()
API_KEY = asyncio.run(databaseManager.fetch_api_key())
hypixel_player_url = f'https://api.hypixel.net/player?key={API_KEY}'

class hypixelAPIManager():
    """
    Class used by the bot to make calls to the hypixel and mojang api.

    THIS CLASS IS CRITICAL TO THE BOT, DO NOT DELETE OR CHANGE WITHOUT MAKING A BACKUP
    """

    def __init__(self) -> None:
        # Defining the api key and other important variable(s), please do not modify
        #self.API_KEY = databaseManager.fetch_api_key(asyncio.run(asyncio.run(databaseManager.connect())))
        self.API_KEY = API_KEY
        self.hypixel_player_url = f'https://api.hypixel.net/player?key={self.API_KEY}'

    async def confirm_name(self, username) -> str:
        async with aiohttp.ClientSession() as res:
            r = await res.get(f'https://api.mojang.com/users/profiles/minecraft/{username}')
            r = await r.json()
        try:
            return r['name']
        except:
            return False

    async def get_username_from_uuid(self, uuid):
        async with aiohttp.ClientSession() as res:
            r = await res.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}')
            r = await r.json()
        try:
            return r['name']
        except:
            return False

    async def get_uuid(self, username) -> str:
        async with aiohttp.ClientSession() as res:
            r = await res.get(f'https://api.mojang.com/users/profiles/minecraft/{username}')
            r = await r.json()
        try:
            return r['id']
        except:
            return False
    
    async def get_discord_account(self, uuid) -> str:
        async with aiohttp.ClientSession() as res:
            url = f'https://api.hypixel.net/player?key={self.API_KEY}&uuid={uuid}'
            player_data = await res.get(f'https://api.hypixel.net/player?key={self.API_KEY}&uuid={uuid}')
            player_data = await player_data.json()

        if player_data['success'] == False:
            return False
        
        elif player_data['player'] == None:
            return False
        
        elif 'socialMedia' not in player_data['player']:
            return False

        discord_account = player_data["player"]["socialMedia"]["links"]["DISCORD"]
        return discord_account

    async def get_discord_account_by_username(self, username) -> str:
        uuid = await hypixelAPI.get_uuid(username)
        if uuid == False:
            return None
        return await hypixelAPI.get_discord_account(uuid)
    
    async def lookup_hypixel_player(self, uuid):
        url = str(hypixel_player_url)
        async with aiohttp.ClientSession() as r:
            data = await r.get(f'{url}&uuid={uuid}')
            data = await data.json()
        return data
    
    async def get_bedwars_level(self, exp):

            xp_reqs = {0: 500, 1: 1000, 2: 2000, 3: 3500, 4: 3500}
            level = 0
            hundreds = 0
            req = 0
            while exp >= req:

                if level in xp_reqs:
                    req = xp_reqs[level]
                else:
                    req = 5000

                exp -= req
                level += 1
                if level == 100:
                    level = 0
                    hundreds += 1
            level += (100*hundreds)
            return level


    async def get_bedwars_stats(self, uuid) -> dict:
        r = await hypixelAPI.lookup_hypixel_player(uuid)
        if r['success'] == False:
            return False
        
        bedwars_stats = r['player']['stats']['Bedwars']

        bw_wins = bedwars_stats['wins_bedwars']
        bw_losses = bedwars_stats['losses_bedwars']
        bw_wlr = bw_wins/bw_losses
        bw_final_deaths = bedwars_stats['final_deaths_bedwars']
        bw_final_kills = bedwars_stats['final_kills_bedwars']
        bw_fkdr = bw_final_kills/bw_final_deaths
        bw_exp = bedwars_stats['Experience']
        bw_stars = await hypixelAPI.get_bedwars_level(bw_exp)
        bw_index = bw_stars*(bw_fkdr**2)

        return {"bw_wins": bw_wins, "bw_losses": bw_losses, "bw_wlr": bw_wlr, "bw_final_kills": bw_final_kills, "bw_final_deaths": bw_final_deaths, "bw_fkdr": bw_fkdr, "bw_stars": bw_stars, "bw_index": bw_index}


    async def get_bedwars_stats_by_username(self, username) -> dict:
        pass

    async def get_duels_stats(self, uuid) -> dict:
        r = await hypixelAPI.lookup_hypixel_player(uuid)
        if r['success'] == False:
            return False
        
        duels_stats = r['player']['stats']['Duels']

        duels_wins = duels_stats['wins']
        duels_losses = duels_stats['losses']
        duels_wlr = duels_wins/duels_losses
        duels_kills = duels_stats['kills']
        duels_deaths = duels_stats['deaths']
        duels_kdr = duels_kills/duels_deaths

        return {"duels_wins": duels_wins, "duels_losses": duels_losses, "duels_wlr": duels_wlr, "duels_kills": duels_kills, "duels_deaths": duels_deaths, "duels_kdr": duels_kdr}

    async def get_duels_stats_by_username(self, username) -> dict:
        pass

    async def get_all_player_info_from_username(self, username):

        try:
            uuid = await hypixelAPI.get_uuid(username)
            discord_account = await hypixelAPI.get_discord_account(uuid)

            return {'success': True, 'uuid': uuid, 'username': username, 'discord': str(discord_account)}
        
        except Exception as e:
            return {'success': False, 'reason': e}
        
    async def get_guild_info(self, guildname):
        pass

    async def get_player_guild(self, uuid):
        pass

    async def get_guild_from_player(self, uuid):
        pass

    async def get_member_gexp_from_guild_member_data(self, guild_members, member_uuid):
        gexp = 0
        for member in guild_members:
            if member['uuid'] == member_uuid:
                expHistory = member['expHistory']
                for i in expHistory:
                    gexp += expHistory[i]
        return gexp
        
        
    async def get_guild_members(self, guildname):
        async with aiohttp.ClientSession() as r:
            guild_data = await r.get(f'https://api.hypixel.net/guild?name={guildname}&key={self.API_KEY}')
            guild_data = await guild_data.json()
        if guild_data['success'] == True:
            guild_members = guild_data['guild']['members']
            return guild_members
        return None
    
    async def get_guild_from_uuid(self, uuid):
        async with aiohttp.ClientSession() as r:
            guild_data = await r.get(f'https://api.hypixel.net/guild?player={uuid}&key={self.API_KEY}')
            guild_data = await guild_data.json()
        if guild_data['success'] == True:
            guild_members = guild_data['guild']
            return guild_members
        return None

    async def get_guild_gexp(self, guildName):
        async with aiohttp.ClientSession() as r:
            guild_data = await r.get(f'https://api.hypixel.net/guild?key={API_KEY}&name={guildName}')
            guild_data = await guild_data.json()
            return guild_data['guild']['exp']
    
hypixelAPI = hypixelAPIManager()
