from sqlalchemy import create_engine, ForeignKey, Column, BigInteger, CHAR, Boolean, event, select, exc, ARRAY, JSON, String, insert
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncAttrs
from config import database_url
from devLogging import devLogging

#For the database, the sqlalchemy library is being used
#Currently, there are some parts of the database that are unused, this is to make it easier to add features later without migrating the database
#Please only add methods/attributes to the databaseManager class, as altering any of the other ones may cause loading failure

Base = declarative_base()

class Member(AsyncAttrs, Base):
    """
    Contains all information relevant to members, including discordID and uuid. The username is also stored but is not used for any identifying features in the bot.
    Please only use the username for cosmetic purposes as it can be changed.
    
    THIS CLASS IS CRITICAL TO THE BOT, DO NOT DELETE OR CHANGE WITHOUT MAKING A BACKUP
    """
    
    __tablename__ = "MEMBERS"

    discordID = Column("discordID", BigInteger, primary_key=True)
    uuid = Column("uuid", String(36))
    username = Column("username", String(16))

    def __init__(self, discordID, uuid, username):

        self.discordID = discordID
        self.uuid = uuid
        self.username = username

    def __repr__(self):
        return f"{self.username}, {self.discordID}, {self.uuid}"
    

class Guild(AsyncAttrs, Base):
    """
    Contains all the basic information that the bot needs to function, including which roles have permissions, where to log events, what the api key is, etc.
    Currently certain columns, 'weekOneGexp', 'weekTwoGexp', 'monitoredGuilds' are unused. These columns currently exist purely to allow features to be added later.
    
    THIS CLASS IS CRITICAL TO THE BOT, DO NOT DELETE OR CHANGE WITHOUT MAKING A BACKUP
    """
    
    __tablename__ = "GUILD"

    guildID = Column("guildID", BigInteger, primary_key=True)
    guildName = Column("guildName", String(36))
    staffRole = Column("staffRole", BigInteger)
    adminRole = Column("adminRole", BigInteger)
    guestRole = Column("guestRole", BigInteger)
    guildMemberRole = Column("guildMemberRole", BigInteger)
    unverifiedRole = Column("unverifiedRole", BigInteger)
    acceptedRole = Column("acceptedRole", BigInteger)
    mvpRole = Column("mvpRole", BigInteger)
    developerRole = Column("developerRole", BigInteger)
    logChannel = Column("logChannel", BigInteger)
    messageLogChannel = Column("messageLogChannel", BigInteger)
    waitingListChannel = Column("waitingListChannel", BigInteger)
    applicationSubmissionsChannel = Column("applicationSubmissionsChannel", BigInteger)
    monitoredGuilds = Column('monitoredGuilds', String(999))
    weekOneGexp = Column("weekOneGexp", JSON)
    weekTwoGexp = Column("weekTwoGexp", JSON)
    weekThreeGexp = Column("weekThreeGexp", JSON)
    apiKey = Column("apiKey", String(36))
    
    def __init__(self, guildID, guildName, staffRole, adminRole, guestRole, guildMemberRole, unverifiedRole, acceptedRole, mvpRole, developerRole, logChannel, messageLogChannel, waitingListChannel, absenceSubmissionsChannel, apiKey, monitoredGuilds='', weekOneGexp={}, weekTwoGexp={}, weekThreeGexp={}):
        self.guildID = guildID
        self.guildName = guildName
        self.staffRole = staffRole
        self.adminRole = adminRole
        self.guestRole = guestRole
        self.guildMemberRole = guildMemberRole
        self.unverifiedRole = unverifiedRole
        self.acceptedRole = acceptedRole
        self.mvpRole = mvpRole
        self.developerRole = developerRole
        self.logChannel = logChannel
        self.messageLogChannel = messageLogChannel
        self.waitingListChannel = waitingListChannel
        self.absenceSubmissionsChannel = absenceSubmissionsChannel
        self.apiKey = apiKey
        self.monitoredGuilds = monitoredGuilds
        self.weekOneGexp = weekOneGexp
        self.weekTwoGexp = weekTwoGexp
        self.weekThreeGexp = weekThreeGexp

    
    def __repr__(self):
        return f""


class Ticket(AsyncAttrs, Base):
    """
    Contains all information regarding tickets. Currently, the bot does not have a ticketing system, however this class is used to store guild applications.
    """

    __tablename__ = "TICKETS"

    channelID = Column("channelID", BigInteger, primary_key=True)
    guildID = Column("guildID", BigInteger)
    ownerID = Column("ownerID", BigInteger)
    panel = Column("panel", String(36))

    def __init__(self, channelID, guildID, ownerID, panel):
        
        self.channelID = channelID
        self.guildID = guildID
        self.ownerID = ownerID
        self.panel = panel

    def __repr__(self):
        return f"{self.channelID}, {self.guildID}, {self.ownerID}, {self.panel}"


class Panel(AsyncAttrs, Base):
    """
    Currently unused, please do not delete as this will be important if a ticketing system is added.
    """

    __tablename__ = "PANELS"

    guildID = Column("guildID", BigInteger)
    categoryID= Column("categoryID", BigInteger)
    panelName = Column("panelName", String(36), primary_key=True)

    def __init__(self, guildID, panelName, categoryID):
        self.guildID = guildID
        self.categoryID = categoryID
        self.panelName = panelName

    def __repr__(self):
        return f"{self.guildID}, {self.categoryID}, {self.panelName}"
    

class MemberGexpHistory(AsyncAttrs, Base):
    """
    Currently unused, please do not delete as this class may be used in the future to track guild member gexp.
    """

    __tablename__ = "MEMBERGEXPHISTORY"

    uuid = Column("uuid", String(36), primary_key=True)
    username = Column("username", String(16))
    thisWeekGexp = Column("thisWeekGexp", JSON)
    weekOneGexp = Column("weekOneGexp", JSON)
    weekTwoGexp = Column("weekTwoGexp", JSON)
    weekThreeGexp = Column("weekThreeGexp", JSON)

    def __init__(self, uuid, username, thisWeekGexp, weekOneGexp, weekTwoGexp, weekThreeGexp):
        self.uuid = uuid
        self.username = username
        self.thisWeekGexp = thisWeekGexp
        self.weekOneGexp = weekOneGexp
        self.weekTwoGexp = weekTwoGexp
        self.weekThreeGexp = weekThreeGexp

    def __repr__(self):
        return f"{self.uuid}, {self.username}, {self.thisWeekGexp}, {self.weekOneGexp}, {self.weekTwoGexp}, {self.weekThreeGexp}"



class databaseManager(AsyncAttrs):
    """
    This class contains methods that are used throughout the bot to interact with the database. 
    
    THIS CLASS IS CRITICAL TO THE BOT, DO NOT DELETE OR CHANGE WITHOUT MAKING A BACKUP
    """
    
    async def connect():
        
        dbEngine = create_async_engine(database_url, pool_recycle=3600, connect_args={'connect_timeout': 30})
        
        dbSessionMaker = async_sessionmaker(bind=dbEngine)
        dbSession = dbSessionMaker()

        return dbSession
    

    async def create_tables():
        """
        Deletes and then recreates all database tables from classes within this file.

        Use of this function *cannot* be undone and will delete *all* information in the database. 
        Do not use unless there is a backup of the database.
        """
        devLogging.database(msg="Beggining to create tables", module=__name__)
        dbEngine = create_engine(database_url)
        sessionMaker = sessionmaker(bind=dbEngine)
        session = sessionMaker()
        devLogging.database(msg="Dropping old tables", module=__name__)
        Base.metadata.drop_all(bind=dbEngine)
        devLogging.database("Dropped old tables, creating new tables", module=__name__)
        Base.metadata.create_all(bind=dbEngine)
        devLogging.database("Created new tables", module=__name__)
        session.commit()
        devLogging.database("Changes committed", module=__name__)


    async def list_tables():
        dbEngine = create_engine(database_url)
        sessionMaker = sessionmaker(bind=dbEngine)
        session = sessionMaker()
        Base.metadata.create_all(bind=dbEngine)
        print(Base.metadata.tables.keys())


    async def fetch_guild_name():
        session = await databaseManager.connect()
        devLogging.database(msg="Fetching guild name", module=__name__)
        try:
            guild = await session.scalar(select(Guild))
            devLogging.database(msg=f"Found guild name: {guild.guildName}", module=__name__)
            await session.close()
            return guild.guildName
        except:
            devLogging.warning(msg="Failed to make query to database for guildName", module=__name__)

    async def register_panel(guildID, panelName, categoryID):
        session = await databaseManager.connect()
        devLogging.database(msg=f"Registering panel: {guildID}, {panelName}, {categoryID}", module=__name__)
        panel = Panel(guildID, panelName, categoryID)
        session.add(panel)
        session.commit()
        devLogging.database(msg=f"Registered panel: {guildID}, {panelName}, {categoryID}", module=__name__)

    
    async def register_member(discordID, uuid, username):
        session = await databaseManager.connect()
        devLogging.database(msg=f"Registering member: {discordID}, {uuid}, {username}", module=__name__)
        member = Member(discordID, uuid, username)
        session.add(member)
        await session.commit()
        devLogging.database(msg=f"Registered member: {discordID}, {uuid}, {username}", module=__name__)
        

    async def register_server(guildID, guildName, staffRole, adminRole, guestRole, guildMemberRole, unverifiedRole, acceptedRole, mvpRole, developerRole, logChannel, messageLogChannel, waitingListChannel, absenceSubmissionsChannel, apiKey):
        session = await databaseManager.connect()
        guild = Guild(guildID, guildName, staffRole, adminRole, guestRole, guildMemberRole, unverifiedRole, acceptedRole, mvpRole, developerRole, logChannel, messageLogChannel, waitingListChannel, absenceSubmissionsChannel, apiKey)
        session.add(guild)
        await session.commit()


    async def fetch_member(discordID):
        session = await databaseManager.connect()
        devLogging.database(msg=f"Fetching member by discordID: {discordID}", module=__name__)
        try:
            member = await session.scalars(select(Member).filter(Member.discordID==discordID))
            member = member.first()
            await session.close()
            return member
        except:
            devLogging.warning(msg=f'Failed to make query to database for the discordID: {discordID}', module=__name__)
            await session.close()

    async def fetch_all_members():
        session = await databaseManager.connect()
        devLogging.database(msg=f"Fetching all registered members", module=__name__)
        members = await session.scalars(select(Member))
        await session.close()
        return members.fetchall()
            


    async def fetch_member_by_username(username):
        session = await databaseManager.connect()
        devLogging.database(msg=f"Fetching member by username: {username}", module=__name__)
        try:
            member = await session.scalars(select(Member).filter(Member.username==username))
            await session.close()
            return member.first()
        except:
            devLogging.warning(msg=f'Failed to make query to database for the username: {username}', module=__name__)
            return None
        


    async def fetch_member_by_uuid(uuid):
        session = await databaseManager.connect()
        try:
            member = await session.scalars(select(Member).filter(Member.uuid==uuid))
            await session.close()
            return member.first()
        except:
            devLogging.warning(msg=f'Failed to make query to database for the uuid: {uuid}', module=__name__)
            return None

    async def delete_member(discordID):
        session = await databaseManager.connect()
        devLogging.database(msg=f"Deleting member by discordID: {discordID}", module=__name__)
        member = await databaseManager.fetch_member(discordID)
        if member != None:
            await session.delete(member)
            devLogging.database(msg=f"Deleted member: {member}", module=__name__)
            await session.commit()

    async def update_member_username(old_member, username):
        session = await databaseManager.connect()
        devLogging.database(msg=f"Updating username for: {old_member} to {username}", module=__name__)
        discordID = old_member.discordID
        member = await session.scalars(select(Member).filter(Member.discordID==discordID))
        member = member.first()
        member.username = username
        details = str(member)
        await session.commit()
        devLogging.database(msg=f"Update finished for user: {details}", module=__name__)

    async def update_member_uuid(member, uuid):
        session = await databaseManager.connect()
        devLogging.database(msg=f"Updating uuid for: {member} to {uuid}", module=__name__)
        member.uuid = uuid
        await session.commit()
        devLogging.database(msg=f"Update finished for user: {member}", module=__name__)

    async def fetch_staff_role():
        session = await databaseManager.connect()
        role = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        await session.close()
        return role.first().staffRole

    async def fetch_admin_role():
        session = await databaseManager.connect()
        role = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        await session.close()
        return role.first().adminRole
    
    async def fetch_accepted_role():
        session = await databaseManager.connect()
        role = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        await session.close()
        return role.first().acceptedRole
    
    async def fetch_unverified_role():
        session = await databaseManager.connect()
        role = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        await session.close()
        return role.first().unverifiedRole
    
    async def fetch_guest_role():
        session = await databaseManager.connect()
        role = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        await session.close()
        return role.first().guestRole
    
    async def fetch_guildMember_role():
        session = await databaseManager.connect()
        role = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        await session.close()
        return role.first().guildMemberRole
    
    async def fetch_mvp_role():
        session = await databaseManager.connect()
        role = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        await session.close()
        return role.first().mvpRole
    
    async def fetch_developer_role():
        session = await databaseManager.connect()
        role = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        await session.close()
        return role.first().developerRole
    
    async def fetch_waitingList_channel():
        session = await databaseManager.connect()
        channel = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        await session.close()
        return channel.first().waitingListChannel
    
    async def fetch_log_channel():
        session = await databaseManager.connect()
        channel = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        await session.close()
        return channel.first().logChannel
    
    async def fetch_messageLog_channel():
        session = await databaseManager.connect()
        channel = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        await session.close()
        return channel.first().messageLogChannel
    

    async def fetch_panel_category(panelName):
        session = await databaseManager.connect()
        category = await session.scalars(select(Panel).filter(Panel.panelName==panelName))
        await session.close()
        return category.first().categoryID
    
    async def register_ticket(channelID, guildID, ownerID, panel):
        session = await databaseManager.connect()
        devLogging.database(msg=f"Registering ticket: {channelID}, {guildID}, {ownerID}, {panel}", module=__name__)
        ticket = Ticket(channelID, guildID, ownerID, panel)
        session.add(ticket)
        await session.commit()

    async def fetch_guild_app(channelID, guildID):
        session = await databaseManager.connect()
        app = await session.scalars(select(Ticket).filter(Ticket.channelID == channelID and Ticket.guildID == guildID and Ticket.panel == "Guild Applications"))
        await session.close()
        return app.first()
    
    async def fetch_guild_app_by_user(ownerID):
        session = await databaseManager.connect()
        app = await session.scalars(select(Ticket).filter(Ticket.ownerID == ownerID))
        await session.close()
        return app.first()

    async def delete_guild_app(channelID, guildID):
        session = await databaseManager.connect()
        app = await databaseManager.fetch_guild_app(channelID, guildID)
        await session.delete(app)
        await session.commit()

    async def update_developer_role(role):
        session = await databaseManager.connect()
        blight = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        blight = blight.first()
        blight.developerRole = role
        await session.commit()

    async def update_admin_role(role):
        session = await databaseManager.connect()
        blight = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        blight = blight.first()
        blight.adminRole = role
        await session.commit()

    async def update_staff_role(role):
        session = await databaseManager.connect()
        blight = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        blight = blight.first()
        blight.staffRole = role
        await session.commit()

    async def update_guildMember_role(role):
        session = await databaseManager.connect()
        blight = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        blight = blight.first()
        blight.guildMemberRole = role
        await session.commit()

    async def update_guest_role(role):
        session = await databaseManager.connect()
        blight = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        blight = blight.first()
        blight.guestRole = role
        await session.commit()

    async def update_accepted_role(role):
        session = await databaseManager.connect()
        blight = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        blight = blight.first()
        blight.first().acceptedRole = role
        await session.commit()

    async def update_unverified_role(role):
        session = await databaseManager.connect()
        blight = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        blight = blight.first()
        blight.unverifiedRole = role
        await session.commit()

    async def update_mvp_role(role):
        session = await databaseManager.connect()
        blight = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        blight = blight.first()
        blight.mvpRole = role
        await session.commit()

    async def fetch_api_key():
        session = await databaseManager.connect()
        key = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        await session.close()
        return key.first().apiKey
    
    async def update_api_key(key):
        session = await databaseManager.connect()
        blight = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        blight = blight.first()
        blight.apiKey = key
        await session.commit()

    async def update_log_channel(channel):
        session = await databaseManager.connect()
        blight = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        blight = blight.first()
        blight.logChannel = channel
        await session.commit()

    async def update_waitingList_channel(channel):
        session = await databaseManager.connect()
        blight = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        blight = blight.first()
        blight.logChannel = channel
        await session.commit()

    async def add_monitoredGuild(guildName):
        monitoredGuilds = await databaseManager.fetch_monitoredGuilds()
        session = await databaseManager.connect()
        monitoredGuilds = f'{monitoredGuilds}, {guildName}'
        if monitoredGuilds.startswith(', '):
            monitoredGuilds = monitoredGuilds[2:]
        blight = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        blight = blight.first()
        blight.monitoredGuilds = monitoredGuilds
        await session.commit()

    async def fetch_monitoredGuilds():
        session = await databaseManager.connect()
        blight = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        await session.close()
        return blight.first().monitoredGuilds


    async def remove_monitoredGuild(guildName):
        session = await databaseManager.connect()
        monitoredGuilds = await databaseManager.fetch_monitoredGuilds()
        guilds = monitoredGuilds.split(', ')
        new_guilds = ''
        for guild in guilds:
            if guildName != guild:
                new_guilds = new_guilds + f', {guild}'
        if monitoredGuilds.startswith(', '):
            monitoredGuilds = monitoredGuilds[2:]
        blight = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        blight = blight.first()
        blight.monitoredGuilds = new_guilds
        await session.commit()

    async def set_monitoredGuilds(guilds):
        session = await databaseManager.connect()
        blight = await session.scalars(select(Guild).filter(Guild.guildName=="Blight"))
        blight = blight.first()
        blight.monitoredGuilds = guilds
        await session.commit()
