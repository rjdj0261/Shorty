import discord
import sentry_sdk
from discord.ext import commands
import psutil
import logging
import platform
import datetime
from enum import Enum
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
import pyshorteners
from firebase_dynamic_links import dynamic_link_builder
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

token = os.environ.get("TOKEN")
sentry = os.environ.get("SENTRY")
log_file = os.environ.get("LOG_FILE")
bitly_key = os.environ.get("BITLY_KEY")
cuttly_key = os.environ.get("CUTTLY_KEY")
shortcm_key = os.environ.get("SHORTCM_KEY")
adfly_key = os.environ.get("ADFLY_KEY")
adfly_uid = os.environ.get("ADFLY_UID")
firebase_key = os.environ.get("FIREBASE_KEY")
prefix = os.environ.get("PREFIX")

# ? Bot Init
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(command_prefix=prefix, intents=intents, help_command=None, application_id=1090517686565470218, status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=f"/help"))
tree = discord.app_commands.CommandTree(bot)

# ? Initiate Sentry
sentry_sdk.init(
    dsn=sentry,
    traces_sample_rate=1.0,
    release="shorty@1.0.0",
    sample_rate=0.25,
    _experiments={"profiles_sample_rate": 1.0},
    debug=True,
    environment="staging",
    max_breadcrumbs=50
)

# ? Initate URLValidator
urlvalidator = URLValidator()

# ? Initiate Logger
logger = logging.getLogger(__name__)

# ? Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler(log_file)
c_handler.setLevel(logging.WARNING)
f_handler.setLevel(logging.ERROR)

# ? Create formatters and add it to handlers
c_format = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
f_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# ? Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

"""
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

# ? Shorteners
class shortners:
    def __init__(self):
        self.isgd = pyshorteners.Shortener().isgd
        self.nullpointer = pyshorteners.Shortener(
            domain="https://0x0.st").nullpointer
        self.bitly = pyshorteners.Shortener(
            api_key=bitly_key).bitly
        self.chilpit = pyshorteners.Shortener().chilpit
        self.clckru = pyshorteners.Shortener().clckru
        self.cuttly = pyshorteners.Shortener(
            api_key=cuttly_key).cuttly
        self.dagd = pyshorteners.Shortener().dagd
        self.osdb = pyshorteners.Shortener().osdb
        self.shortcm = pyshorteners.Shortener(
            api_key=shortcm_key, domain="3adu.short.gy"
        ).shortcm
        self.tinyurl = pyshorteners.Shortener().tinyurl
        self.adfly = pyshorteners.Shortener(
            api_key=adfly_key,
            user_id=adfly_uid,
            domain="test.us",
            group_id=12,
            type="int",
        )
        self.firebase = dynamic_link_builder(
            api_key=firebase_key)

    def req(self, api, link):
        if api == "exeio":
            try:
                req = requests.get(
                    f"https://exe.io/api?api=afe5d717ef19304362234cf6f6b3d934ab0d1a07&url={link}").json()["shortenedUrl"]
                return req
            except:
                return "AN ERROR OCCURED"
        elif api == "gplinks":
            try:
                req = requests.get(
                    f"https://gplinks.in/api?api=eeebc0507eb61fbd079041825d73a5ddb80a7a20&url={link}").json()["shortenedUrl"]
                return req
            except:
                return "AN ERROR OCCURED"
        elif api == "zagl":
            try:
                req = requests.get(f"").json()["shortenedUrl"]
                return req
            except:
                return "AN ERROR OCCURED"
        elif api == "zagl":
            try:
                req = requests.get(
                    f"https://za.gl/api?api=00240505bb426a55e0b1b57bcb0b02cb16d329d3&url={link}").json()["shortenedUrl"]
                return req
            except:
                return "AN ERROR OCCURED"
        elif api == "earn4clicks":
            try:
                req = requests.get(
                    f"https://earn4clicks.in/api?api=a9fd295d6d92818d4e8db9b854ab46f167838c4f&url={link}").json()["shortenedUrl"]
                return req
            except:
                return "AN ERROR OCCURED"
        elif api == "shortest":
            try:
                req = json.loads(requests.put("https://api.shorte.st/v1/data/url", {"urlToShorten": link}, headers={
                                 "public-api-token": "dfa6329d5e397972dd919233b89d8b6f"}).content)["shortenedUrl"]
                return req
            except:
                return "AN ERROR OCCURED"
        elif api == "vurl":
            try:
                req = requests.get(
                    f"https://vurl.com/api.php?url={link}").text
                return req
            except:
                return "AN ERROR OCCURED"
        elif api == "rebrandly":
            linkRequest = {
                "destination": link, "domain": {"fullName": "rebrand.ly"}}
            requestHeaders = {
                "Content-type": "application/json",
                "apikey": "6053520de6be4edc9df4a55a95fc2949",
            }
            req = requests.post("https://api.rebrandly.com/v1/links",
                                data=json.dumps(linkRequest),
                                headers=requestHeaders)
            if (req.status_code == requests.codes.ok):
                newurl = req.json()
                return newurl
            else:
                return "AN ERROR OCCURED"

# ? Initiate Shorteners
shortner = shortners()

# ? On Ready Event
@bot.event
async def on_ready():
    await tree.sync()
    print(
        """
                        _______           _______  _______ _________         
                        (  ____ \|\     /|(  ___  )(  ____ )\__   __/|\     /|
                        | (    \/| )   ( || (   ) || (    )|   ) (   ( \   / )
                        | (_____ | (___) || |   | || (____)|   | |    \ (_) / 
                        (_____  )|  ___  || |   | ||     __)   | |     \   /  
                              ) || (   ) || |   | || (\ (      | |      ) (   
                        /\____) || )   ( || (___) || ) \ \__   | |      | |   
                        \_______)|/     \|(_______)|/   \__/   )_(      \_/  """
    )
    print("=" * 40, "System Information", "=" * 40)
    uname = platform.uname()
    print(f"System: {uname.system}")
    print(f"Node Name: {uname.node}")
    print(f"Release: {uname.release}")
    print(f"Version: {uname.version}")
    print(f"Machine: {uname.machine}")
    print(f"Processor: {uname.processor}")
    # 52
    # Boot Time
    print("=" * 40, "Boot Time", "=" * 40)
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.datetime.fromtimestamp(boot_time_timestamp)
    print(
        f"Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}")

    # let's print CPU information
    print("=" * 40, "CPU Info", "=" * 40)
    # number of cores
    print("Physical cores:", psutil.cpu_count(logical=False))
    print("Total cores:", psutil.cpu_count(logical=True))
    # CPU frequencies
    cpufreq = psutil.cpu_freq()
    print(f"Max Frequency: {cpufreq.max:.2f}Mhz")
    print(f"Min Frequency: {cpufreq.min:.2f}Mhz")
    print(f"Current Frequency: {cpufreq.current:.2f}Mhz")
    print(f"Total CPU Usage: {psutil.cpu_percent()}%")

    # Memory Information
    print("=" * 40, "Memory Information", "=" * 40)
    # get the memory details
    svmem = psutil.virtual_memory()
    print(f"Total: {get_size(svmem.total)}")
    print(f"Available: {get_size(svmem.available)}")
    print(f"Used: {get_size(svmem.used)}")
    print(f"Percentage: {svmem.percent}%")
    print("=" * 40, "Logs", "=" * 40)
    logger.warning("We have logged in as {0.user}".format(bot))

# ? Error Handler
@bot.event
async def on_command_error(interaction : discord.Interaction, error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        return  # Return because we don't want to show an error for every command not found
    elif isinstance(error, commands.CommandOnCooldown):
        message = f"This command is on cooldown. Please try again after {round(error.retry_after, 1)} seconds."
    elif isinstance(error, commands.MissingPermissions):
        message = "You are missing the required permissions to run this command!"
    elif isinstance(error, commands.UserInputError):
        message = f"Something about your input was wrong, please ensure the you use ```?command (link)``` check your input and try again!"
    else:
        message = "Oh no! Something went wrong while running the command!"
        await bot.get_channel(1090745096040894604).send(error)
        logger.error(error)
        
    await interaction.response.send_message(message, delete_after=5)

# ? Adfly
@tree.command(description="Shorten your link using adfly!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def adfly(interaction : discord.Interaction, link : str):
    try:
        urlvalidator(link)
        embed = discord.discord.Embed(title=shortner.adfly.short(link), color=0x0055FF).set_footer(
            text="Requested By " + interaction.user.name
        )
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")

# ? Firebase
@tree.command(description="Shorten your link using firebase!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def firebase(interaction : discord.Interaction, link : str):
    try:
        urlvalidator(link)
        options = {
            'link': link,
            'apn': 'com.example.android',
            'ibi': 'com.example.ios'
        }
        embed = discord.discord.Embed(title=shortner.firebase.generate_short_link(app_code='pocketurl', **options), color=0x0055FF).set_footer(
            text="Requested By " + interaction.user.name
        )
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")

# ? Nullpointer
@tree.command(description="Shorten your link using nullpointer!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def nullpointer(interaction : discord.Interaction, link : str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.nullpointer.short(link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")

# ? Exeio
@tree.command(description="Shorten your link using exeio!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def exeio(interaction : discord.Interaction, link : str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.req("exeio", link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Vurl
@tree.command(description="Shorten your link using vurl!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def vurl(interaction : discord.Interaction, link : str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.req("vurl", link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Rebrandly
@tree.command(description="Shorten your link using rebrandly!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def rebrandly(interaction : discord.Interaction, link : str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.req("rebrandly", link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Shortest
@tree.command(description="Shorten your link using shortest!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def shortest(interaction : discord.Interaction, link : str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.req("shortest", link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Earn4clicks
@tree.command(description="Shorten your link using earn4clicks!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def earn4clicks(interaction : discord.Interaction, link : str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.req("earn4clicks", link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Gplinks
@tree.command(description="Shorten your link using gplinks!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def gplinks(interaction : discord.Interaction, link : str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.req("gplinks", link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Zagl
@tree.command(description="Shorten your link using zagl!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def zagl(interaction : discord.Interaction, link : str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.req("zagl", link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Isgd
@tree.command(description="Shorten your link using isgd!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def isgd(interaction : discord.Interaction, link : str):
    try:
        urlvalidator(link)
        embed = discord.Embed(title=shortner.isgd.short(link), color=0x0055FF).set_footer(
            text="Requested By " + interaction.user.name
        )
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Bitly
@tree.command(description="Shorten your link using bitly!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def bitly(interaction : discord.Interaction, link : str):
    try:
        urlvalidator(link)
        embed = discord.Embed(title=shortner.bitly.short(link), color=0x0055FF).set_footer(
            text="Requested By " + interaction.user.name
        )
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Chilpit
@tree.command(description="Shorten your link using chilpit!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def chilpit(interaction : discord.Interaction, link : str):
    try:
        urlvalidator(link)
        embed = discord.Embed(title=shortner.chilpit.short(link), color=0x0055FF).set_footer(
            text="Requested By " + interaction.user.name
        )
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Clckru
@tree.command(description="Shorten your link using clckru!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def clckru(interaction : discord.Interaction, link : str):
    try:
        urlvalidator(link)
        embed = discord.Embed(title=shortner.clckru.short(link), color=0x0055FF).set_footer(
            text="Requested By " + interaction.user.name
        )
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Cuttly
@tree.command(description="Shorten your link using cuttly!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def cuttly(interaction : discord.Interaction, link : str):
    try:
        urlvalidator(link)
        embed = discord.Embed(title=shortner.cuttly.short(link), color=0x0055FF).set_footer(
            text="Requested By " + interaction.user.name
        )
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Dagd
@tree.command(description="Shorten your link using dagd!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def dagd(interaction : discord.Interaction, link : str):
    try:
        urlvalidator(link)
        embed = discord.Embed(title=shortner.dagd.short(link), color=0x0055FF).set_footer(
            text="Requested By " + interaction.user.name
        )
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Osdb
@tree.command(description="Shorten your link using osdb!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def osdb(interaction : discord.Interaction, link : str):
    try:
        urlvalidator(link)
        embed = discord.Embed(title=shortner.osdb.short(link), color=0x0055FF).set_footer(
            text="Requested By " + interaction.user.name
        )
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Shortcm
@tree.command(description="Shorten your link using shortcm!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def shortcm(interaction : discord.Interaction, link : str):
    try:
        urlvalidator(link)
        embed = discord.Embed(title=shortner.shortcm.short(link), color=0x0055FF).set_footer(
            text="Requested By " + interaction.user.name
        )
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Tinyurl
@tree.command(description="Shorten your link using tinyurl!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def tinyurl(interaction : discord.Interaction, link : str):
    try:
        urlvalidator(link)
        embed = discord.Embed(title=shortner.tinyurl.short(link), color=0x0055FF).set_footer(
            text="Requested By " + interaction.user.name
        )
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")

# ? Guildlist (Owner Only)
@tree.command(description="Get list of servers shorty is in!")
@commands.bot_has_permissions(attach_files=True)
async def guildlist(interaction : discord.Interaction):
    if interaction.user.id == 829232267658264607:
        with open("guildlist.csv", "w") as guild_list:
            guild_list.write("Server ID,Server Name,# of Users,Features\n")
            for guild in bot.guilds:
                # Write to csv file (guild name, total member count, region and features)
                guild_list.write(
                    f'{guild.id},"{guild.name}",{guild.member_count},{guild.features}\n'
                )

        await interaction.response.send_message(file=discord.File("guildlist.csv"))
    else: await interaction.response.send_message("You need to be the owner of the bot to run this command!")

# ? Invite
@tree.command(description="Invite shorty to your server!")
async def invite(interaction : discord.Interaction):
    embed = discord.Embed(
        title="Invite The Bot",
        description=f"[https://dsc.gg/shorty](https://dsc.gg/shorty)",
        color=0x0055FF,
    ).set_footer(text="Requested By " + interaction.user.name)
    await interaction.response.send_message(embed=embed)

# ? Support
@tree.command(description="Join shorty's support server!")
async def support(interaction : discord.Interaction):
    embed = discord.Embed(
        title="Join The Support Server",
        description=f'[https://dsc.gg/shorty-support](https://dsc.gg/shorty-support)',
        color=0x0055FF,
    ).set_footer(text="Requested By " + interaction.user.name)
    await interaction.response.send_message(embed=embed)

# ? Ping
@tree.command(description="Join shorty's support server!")
async def ping(interaction : discord.Interaction):
    embed = (
        discord.Embed(color=0x0055FF)
        .add_field(name="Ping", value=bot.latency, inline=False)
        .set_footer(text="Requested By " + interaction.user.name))
    await interaction.response.send_message(embed=embed)

# ? Suggest
@tree.command(description="Give us your valuable suggestions!")
@discord.app_commands.describe(suggestion="Suggestion you would like to give!")
async def suggest(interaction : discord.Interaction, suggestion : str):
    embed = discord.Embed(title=suggestion, color=0x0055FF).set_author(
        name=interaction.user.name)
    await bot.fetch_channel(1090758793501085696).send(embed=embed)

# ? Help
@tree.command(description="Get list of commands!")
async def help(interaction : discord.Interaction):
    embed = discord.Embed(
        title="List Of Commands",
        description="Every Command Has A Cooldown of 30 seconds!",
        color=0x0055FF,
    )
    embed.add_field(
        name="adfly", value="Shorten Your Link Using Adfly.", inline=False
    )
    embed.add_field(
        name="nullpointer", value="Shorten Your Link Using Nullpointer.", inline=False
    )
    embed.add_field(
        name="isgd", value="Shorten Your Link Using Isgd.", inline=False
    )
    embed.add_field(
        name="bitly", value="Shorten Your Link Using Bitly.", inline=False
    )
    embed.add_field(
        name="chilpit", value="Shorten Your Link Using Chilpit.", inline=False
    )
    embed.add_field(
        name="clckru", value="Shorten Your Link Using Clckru.", inline=False
    )
    embed.add_field(
        name="cuttly", value="Shorten Your Link Using Cuttly.", inline=False
    )
    embed.add_field(
        name="dagd", value="Shorten Your Link Using Dagd.", inline=False
    )
    embed.add_field(
        name="osdb", value="Shorten Your Link Using Osdb.", inline=False
    )
    embed.add_field(
        name="shortcm", value="Shorten Your Link Using Shortcm.", inline=False
    )
    embed.add_field(
        name="tinyurl", value="Shorten Your Link Using Tinyurl.", inline=False
    )
    embed.add_field(
        name="exeio", value="Shorten Your Link Using Exeio.", inline=False
    )
    embed.add_field(
        name="rebrandly", value="Shorten Your Link Using Rebrandly.", inline=False
    )
    embed.add_field(
        name="gplinks", value="Shorten Your Link Using Gplinks.", inline=False
    )
    embed.add_field(
        name="zagl", value="Shorten Your Link Using Zagl.", inline=False
    )
    embed.add_field(
        name="shortest", value="Shorten Your Link Using Shortest.", inline=False
    )
    embed.add_field(
        name="earn4clicks", value="Shorten Your Link Using Earn4clicks.", inline=False
    )
    embed.add_field(
        name="vurl", value="Shorten Your Link Using Vurl.", inline=False
    )
    embed.add_field(
        name="firebase", value="Shorten Your Link Using Shorty's Firebase.", inline=False
    )
    embed.add_field(
        name="invite", value="Invite The Bot To Your Server", inline=False
    )
    embed.add_field(
        name="suggest", value="Send A Suggestion To The Developer Of The Bot", inline=False
    )
    embed.add_field(
        name="support", value="Join The Support Server Of The Bot", inline=False
    )
    embed.add_field(
        name="ping", value="Ping Of The Bot", inline=False
    )
    embed.set_footer(
        text="Requested By " + interaction.user.name
    )
    await interaction.response.send_message(embed=embed)

bot.run("")
