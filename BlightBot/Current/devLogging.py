import colorama
from colorama import Fore
import time
import datetime

colorama.init(autoreset=True)

warning_colour = Fore.YELLOW
log_colour = Fore.LIGHTBLUE_EX
error_colour = Fore.LIGHTRED_EX
reset_colour = Fore.RESET
module_colour = Fore.MAGENTA
time_colour = Fore.WHITE
event_colour = Fore.LIGHTMAGENTA_EX
db_colour = Fore.LIGHTGREEN_EX

class devLogging:

    def warning(msg='UNLABALED WARNING', module='Unknown'):
        """
        For errors that are not urgent and are not expected to repeat long term, such as being ratelimited by hypixel api or having to reconnect to the database
        """
        print(f'{time_colour}{datetime.datetime.now()}{reset_colour} {warning_colour}WARNING{reset_colour}    {module_colour}{module}{reset_colour} {msg}')

    def error(msg='UNLABALED ERROR', module='Unknown'):
        """
        For urgent errors that effect the general functionality of the bot, such as having an invalid api key or being unable to log into the database
        """
        print(f'{time_colour}{datetime.datetime.now()}{reset_colour} {error_colour}ERROR{reset_colour}    {module_colour}{module}{reset_colour} {msg}')

    def info(msg='UNLABALED INFO', module='Unknown'):
        """
        General logs, this should be used for things such as function that run on startup (loading cogs, connecting to database) and scheduled status reports
        """
        print(f'{time_colour}{datetime.datetime.now()}{reset_colour} {log_colour}INFO{reset_colour}    {module_colour}{module}{reset_colour} {msg}')

    def event(msg='UNLABELED EVENT', module='Unknown'):
        """
        For discord events and api events that are not tied to startup, such as a command being run, a channel being deleted, making a query to the hypixel api, etc
        """
        print(f'{time_colour}{datetime.datetime.now()}{reset_colour} {event_colour}EVENT{reset_colour}    {module_colour}{module}{reset_colour} {msg}')

    def database(msg='UNLABELED EVENT', module='UNKNOWN'):
        """
        For events connected to the database, including queries, writes, etc
        """
        print(f'{time_colour}{datetime.datetime.now()}{reset_colour} {db_colour}DATABASE{reset_colour}    {module_colour}{module}{reset_colour} {msg}')
