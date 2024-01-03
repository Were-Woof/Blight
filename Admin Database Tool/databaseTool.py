from sqlalchemy import create_engine, ForeignKey, Column, BigInteger, CHAR, Boolean, event, select, exc, ARRAY, JSON, String, insert, text
from sqlalchemy.orm import sessionmaker, declarative_base

database_password = ''
database_username = ''
database_name = ''
database_endpoint = ''
database_url = f'mysql://{database_username}:{database_password}@{database_endpoint}/{database_name}'

Base = declarative_base()

class Member(Base):
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
    

class Guild(Base):
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


class Ticket(Base):
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


class Panel(Base):
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
    

class MemberGexpHistory(Base):
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

class databaseBackend():
    
    def connect(url):
        dbEngine = create_engine(url)
        
        dbSessionMaker = sessionmaker(bind=dbEngine)
        session = dbSessionMaker()

        return session
    
    def list_all_tables():
        dbEngine = create_engine(database_url)
        sessionMaker = sessionmaker(bind=dbEngine)
        session = sessionMaker()
        tables = Base.metadata.tables.keys()

        return tables
    
    def list_all_columns(session, table):

        result = session.execute(text(f"SELECT * FROM {table}"))

        return result.keys()
    
    def fetch_data_from_table(session, table, column, row):

        result = session.execute(text(f"SELECT * FROM {table} WHERE {column}={row}"))

        return result.fetchall()[0]
    
    def fetch_all_data_from_table(session, table, column=None):
        
        if column != None:
            result = session.execute(text(f"SELECT {column} FROM {table}"))
        else:
            result = session.execute(text(f"SELECT * FROM {table}"))

        return result.fetchall()
    
    def write(session, table, args):
        
        columns = databaseBackend.list_all_columns(session, table)

        args = tuple(args)

        if len(args) != (len(columns)):
            print(f'Unexpected number of values: {len(args)} when {len(columns)} are required')
            return

        msg = f"INSERT INTO {table} ("

        for column in columns:
            msg = msg + f'{column}, '

        msg = msg[0:-2]
        msg = msg + ') VALUES ('

        for arg in args:
            msg = msg + f'{arg}, '
        msg = msg[0:-2]
        msg = msg + ')'

        sql = text(msg)


        session.execute(sql)
        session.commit()

    def delete(session, table, column, value):

        sql = text(f'DELETE FROM {table} WHERE {column}={value}')

        sure = input('Are you sure you want to do this? (y/n)')
        if sure.lower() not in ('y', 'ye', 'yes', 'true', 'confirm', 'yep'):
            print('Command cancelled')
            return

        session.execute(sql)
        session.commit()
        

class databaseTool():

    def __init__(self):

        self.session = None
        

    def main(self):

        print("Starting..")
        print('Logging in..')
        self.session = databaseBackend.connect(database_url)
        print('Logged in successfully')
        msg = """

Database tool v1.0.0 started.

This is an admin tool for the blight bot database. This tool is connected to a live database being used in the blight discord server. This tool is not a toy, so please don't use it as one.
To see a list of all available commands, type 'help'. If you need further support, please contact this tool's developer.
As this is designed for admin and developer use, there is not a large amount of error handling, so you may see some errors in terminal. If you see any error messages, it probably means that we are not able to connect to the database, or you made a bad request, so check your commands for typo's.
            """

        while True:
            try:
                cmd = input('>> ')

                self.read_input(cmd)
            except Exception as e:
                print(e)

    def read_input(self, cmd):
        raw_command = cmd
        cmd = cmd.split(' ')
        
        if cmd[0] == 'help':
            cmd.remove('help')
            self.help(cmd)
        
        elif cmd[0] == 'tables':
            cmd.remove('tables')
            self.tables(cmd)

        elif cmd[0] == 'columns':
            cmd.remove('columns')
            self.columns(cmd)

        elif cmd[0] == 'fetch':
            cmd.remove('fetch')
            self.fetch(cmd)

        elif cmd[0] == 'fetchall':
            cmd.remove('fetchall')
            self.fetchall(cmd)

        elif cmd[0] == 'refresh':
            cmd.remove('refresh')
            self.refresh(cmd)
        
        elif cmd[0] == 'write':
            cmd.remove('write')
            databaseBackend.write(self.session, cmd[0], cmd[1:])

        elif cmd[0] == 'delete':
            cmd.remove('delete')
            self.delete(cmd)


    def help(self, command=None):

        command_lst = {
                    "help": "Sends help information about a specific command, if no command is designated this message is sent.\nSyntax: help <command=None>",
                       
                    "tables": "Lists all tables in the connected database.\nSyntax: tables",
                       
                    "columns": "Lists all columns in a designated table.\nSyntax: columns <table>",
                       
                    "fetch": "Fetches the first row from a table found where a particular column holds a designated value.\nSyntax: fetch <table> <column> <value>",

                    "fetchall": "Fetches all rows from a particular table. If a column is selected then only the rows in that column are fetched.\nSyntax: fetch <table> <column> <value>",

                    "delete": "Delete a row in the database that has a particular column value.\nSyntax: delete <table> <column> <value>",
                       
                    "write": "Create a row in a table with designated values. Use the columns command to determine what data you need to input\nSyntax: write <value1> <value2> <value3>..\nExample: write Member id=13 age=19 name='Pineapple'",
                       
                    "refresh": "Refreshes connection to the database.\nSyntax: Refresh",                 
                        }
        
        if command == []:
            msg = 'Available commands:'
            for cmd in command_lst:
                msg = msg + f'   {cmd}'
            print(msg)
        
        for cmd in command:
            if cmd in command_lst:
                print(f'{cmd}: {command_lst[cmd]}')
            else:
                print(f'Command {cmd} not found')
    
    def tables(self, args=[]):
        if len(args) != 0:
            return
        
        tables = databaseBackend.list_all_tables()
        msg = f'Found {len(tables)} tables:'
        for table in tables:
            msg = msg + f'\n   {table}'
        
        print(msg)

    def columns(self, args=[]):
        if len(args) == 0:
            print('You need to specify a table when using this command')
            return
        
        for table in args:
            if len(table) > 1:
                columns = databaseBackend.list_all_columns(self.session, table)

                msg = f'Found {len(columns)} columns in table {table}:'
                for column in columns:
                    msg = msg + f'\n   {column}'
        
                print(msg)

    def fetch(self, args=[]):
        if len(args) == 0:
            print('You need to provide more arguments when using this command')
            return
        
        data = databaseBackend.fetch_data_from_table(self.session, args[0], args[1], args[2])

        columns = databaseBackend.list_all_columns(self.session, args[0])

        space = ' '
        msg = ''

        for column in columns:
            msg = msg + f'{column}{space*(40-len(column))}'
        msg = msg + '\n\n'

        for detail in data:
            msg = msg + f'{detail}{space*(40-len(str(detail)))}'
        print(msg)

    def fetchall(self, args=[]):
        if len(args) == 0:
            print('You need to provide more arguments when using this command')
            return
        
        elif len(args) == 1:
            data = databaseBackend.fetch_all_data_from_table(self.session, args[0])
            columns = databaseBackend.list_all_columns(self.session, args[0])

            space = ' '
            msg = ''
            for column in columns:
                msg = msg + f'{column}{space*(40-len(column))}'
            msg = msg + '\n\n'
            for row in data:
                for detail in row:
                    msg = msg + f'{detail}{space*(40-len(str(detail)))}'
                msg = msg + '\n'
            print(msg)
        
        
        elif len(args) < 2:
            print('This command only takes up to two arguments')
            return
        else:
            data = databaseBackend.fetch_all_data_from_table(self.session, args[0], args[1])
            msg = f'{args[1]}\n'
            for row in data:
                msg = msg + f'{row[0]}\n'
            print(msg)

    
    def delete(self, args):
        if len(args) != 3:
            print('You did not enter the correct amount of arguments for this command. This command takes 3 arguments.')
            return

        databaseBackend.delete(self.session, args[0], args[1], args[2])
        print('Data deleted')

    def refresh(self, args):
        if len(args) != 0:
            print('This command does not take any arguments')
            return
        
        self.session = databaseBackend.connect(url=database_url)
        print('Session refreshed')
       


if __name__ == '__main__':

    app = databaseTool()
    app.main()
