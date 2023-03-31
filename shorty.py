import discord
from sentry_sdk import init as sentry_init
from discord.ext import commands
from psutil import boot_time, cpu_count, cpu_freq, cpu_percent, virtual_memory
import logging
import platform
from datetime import datetime
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
import pyshorteners
from firebase_dynamic_links import dynamic_link_builder as dlb
import requests
from json import dumps, loads
from aioredis import from_url
from dotenv import load_dotenv
from better_help import Help

load_dotenv()

class Settings():
    """A class that manages all settings from .env file"""
    from os import environ
    token = environ.get("TOKEN")
    sentry = environ.get("SENTRY")
    log_file = environ.get("LOG_FILE")
    bitly_key = environ.get("BITLY_KEY")
    cuttly_key = environ.get("CUTTLY_KEY")
    shortcm_key = environ.get("SHORTCM_KEY")
    adfly_key = environ.get("ADFLY_KEY")
    adfly_uid = environ.get("ADFLY_UID")
    firebase_key = environ.get("FIREBASE_KEY")
    prefix = environ.get("PREFIX")
    redis_url = environ.get("REDIS_URL")
    application_id = environ.get("APPLICATION_ID")
    shard_id = environ.get("SHARD_ID")

class Premium_Manager():
    """A class that manages premium users"""
    async def premium_list_update(self, premium_list : list):
        """Updates premium list after changes

        Args:
            premium_list (list): list of premium ids
        """
        premium_str = ""
        for i in premium_list:
            premium_str += (i + " ")
        await redis.set("premium", premium_str)

    async def premium_list_gen(self):
        """Generates Premium List and returns it.

        Returns:
            premium_list: list containing premium ids
        """
        premium_str = await redis.get("premium")
        premium_list = premium_str.split(" ")
        return premium_list

    async def premium_check(self, id : int):
        """Checks if user is premium

        Args:
            id (int): User id

        Returns:
            bool : True if premium user and False if not
        """
        premium_list = await self.premium_list_gen()
        if str(id) in premium_list:
            return True
        else: return False

    async def add_user(self, id : int):
        """Gives User Premium

        Args:
            id (int): User id
        """
        check = await self.premium_check(id)
        premium_list = await self.premium_list_gen()
        if check:
            pass
        else:
            premium_list.append(str(id))
        await self.premium_list_update(premium_list)

    async def rm_user(self, id : int):
        """Removes User Premium

        Args:
            id (int): User id
        """
        check = await self.premium_check(id)
        premium_list = await self.premium_list_gen()
        if check:
            premium_list.remove(str(id))
        else: pass
        await self.premium_list_update(premium_list)

class Shortners:
    """Link Shortner Class"""
    def __init__(self):
        self.isgd = pyshorteners.Shortener().isgd
        self.nullpointer = pyshorteners.Shortener(domain="https://0x0.st").nullpointer
        self.bitly = pyshorteners.Shortener(api_key=settings.bitly_key).bitly
        self.chilpit = pyshorteners.Shortener().chilpit
        self.clckru = pyshorteners.Shortener().clckru
        self.cuttly = pyshorteners.Shortener(api_key=settings.cuttly_key).cuttly
        self.dagd = pyshorteners.Shortener().dagd
        self.osdb = pyshorteners.Shortener().osdb
        self.shortcm = pyshorteners.Shortener(
            api_key=settings.shortcm_key, domain="3adu.short.gy"
        ).shortcm
        self.tinyurl = pyshorteners.Shortener().tinyurl
        self.adfly = pyshorteners.Shortener(
            api_key=settings.adfly_key,
            user_id=settings.adfly_uid,
            domain="test.us",
            group_id=12,
            type="int",
        )
        self.firebase = dlb(api_key=settings.firebase_key)

    def req(self, api, link):
        """Shortener Request Method"""
        if api == "exeio":
            try:
                req = requests.get(
                    f"https://exe.io/api?api=afe5d717ef19304362234cf6f6b3d934ab0d1a07&url={link}"
                ).json()["shortenedUrl"]
                return req
            except:
                return "AN ERROR OCCURED"
        elif api == "gplinks":
            try:
                req = requests.get(
                    f"https://gplinks.in/api?api=eeebc0507eb61fbd079041825d73a5ddb80a7a20&url={link}"
                ).json()["shortenedUrl"]
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
                    f"https://za.gl/api?api=00240505bb426a55e0b1b57bcb0b02cb16d329d3&url={link}"
                ).json()["shortenedUrl"]
                return req
            except:
                return "AN ERROR OCCURED"
        elif api == "earn4clicks":
            try:
                req = requests.get(
                    f"https://earn4clicks.in/api?api=a9fd295d6d92818d4e8db9b854ab46f167838c4f&url={link}"
                ).json()["shortenedUrl"]
                return req
            except:
                return "AN ERROR OCCURED"
        elif api == "shortest":
            try:
                req = loads(
                    requests.put(
                        "https://api.shorte.st/v1/data/url",
                        {"urlToShorten": link},
                        headers={
                            "public-api-token": "dfa6329d5e397972dd919233b89d8b6f"
                        },
                    ).content
                )["shortenedUrl"]
                return req
            except:
                return "AN ERROR OCCURED"
        elif api == "vurl":
            try:
                req = requests.get(f"https://vurl.com/api.php?url={link}").text
                return req
            except:
                return "AN ERROR OCCURED"
        elif api == "rebrandly":
            linkRequest = {"destination": link, "domain": {"fullName": "rebrand.ly"}}
            requestHeaders = {
                "Content-type": "application/json",
                "apikey": "6053520de6be4edc9df4a55a95fc2949",
            }
            req = requests.post(
                "https://api.rebrandly.com/v1/links",
                data=dumps(linkRequest),
                headers=requestHeaders,
            )
            if req.status_code == requests.codes.ok:
                newurl = req.json()
                return newurl
            else:
                return "AN ERROR OCCURED"

def get_size(bytes, suffix="B"):
    """
        Scale bytes to its proper format
        e.g:
            1253656 => '1.20MB'
            1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

# ? Premium Manager Init
premium_manager = Premium_Manager()

# ? Settings Init
settings = Settings()

# ? Redis Init
redis = from_url(settings.redis_url)

# ? Bot Init
intents = discord.Intents.default()
intents.message_content = True
bot = commands.AutoShardedBot(
    shard_id=settings.shard_id,
    command_prefix=settings.prefix,
    intents=intents,
    help_command=Help(),
    application_id=settings.application_id,
    status=discord.StaHes.online,
    activity=discord.Activity(type=discord.ActivityType.watching, name=f"/help"),
)

# ? Initiate Sentry
sentry_init(
    dsn=settings.sentry,
    traces_sample_rate=1.0,
    release="shorty@1.0.0",
    sample_rate=0.25,
    _experiments={"profiles_sample_rate": 1.0},
    environment="staging",
    max_breadcrumbs=50,
)

# ? Initate URLValidator
urlvalidator = URLValidator()

# ? Initiate Logger
logger = logging.getLogger(__name__)

# ? Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler(settings.log_file)
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

# ? Initiate Shorteners
shortner = Shortners()

# ? On Ready Event
@bot.event
async def on_ready():
    await bot.tree.sync()
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
    boot_time_timestamp = boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    print(f"Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}")

    # let's print CPU information
    print("=" * 40, "CPU Info", "=" * 40)
    # number of cores
    print("Physical cores:", cpu_count(logical=False))
    print("Total cores:", cpu_count(logical=True))
    # CPU frequencies
    cpufreq = cpu_freq()
    print(f"Max Frequency: {cpufreq.max:.2f}Mhz")
    print(f"Min Frequency: {cpufreq.min:.2f}Mhz")
    print(f"Current Frequency: {cpufreq.current:.2f}Mhz")
    print(f"Total CPU Usage: {cpu_percent()}%")

    # Memory Information
    print("=" * 40, "Memory Information", "=" * 40)
    # get the memory details
    svmem = virtual_memory()
    print(f"Total: {get_size(svmem.total)}")
    print(f"Available: {get_size(svmem.available)}")
    print(f"Used: {get_size(svmem.used)}")
    print(f"Percentage: {svmem.percent}%")
    print("=" * 40, "Logs", "=" * 40)
    logger.warning("We have logged in as {0.user}".format(bot))


# ? Error Handler
@bot.event
async def on_command_error(
    interaction: discord.Interaction, error: commands.CommandError
):
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
@bot.tree.command(description="Shorten your link using adfly!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def adfly(interaction: discord.Interaction, link: str):
    try:
        urlvalidator(link)
        embed = discord.discord.Embed(
            title=shortner.adfly.short(link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Firebase
@bot.tree.command(description="Shorten your link using firebase!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def firebase(interaction: discord.Interaction, link: str):
    try:
        urlvalidator(link)
        options = {"link": link, "apn": "com.example.android", "ibi": "com.example.ios"}
        embed = discord.discord.Embed(
            title=shortner.firebase.generate_short_link(
                app_code="pocketurl", **options
            ),
            color=0x0055FF,
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Nullpointer
@bot.tree.command(description="Shorten your link using nullpointer!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def nullpointer(interaction: discord.Interaction, link: str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.nullpointer.short(link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Exeio
@bot.tree.command(description="Shorten your link using exeio!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def exeio(interaction: discord.Interaction, link: str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.req("exeio", link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Vurl
@bot.tree.command(description="Shorten your link using vurl!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def vurl(interaction: discord.Interaction, link: str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.req("vurl", link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Rebrandly
@bot.tree.command(description="Shorten your link using rebrandly!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def rebrandly(interaction: discord.Interaction, link: str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.req("rebrandly", link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Shortest
@bot.tree.command(description="Shorten your link using shortest!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def shortest(interaction: discord.Interaction, link: str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.req("shortest", link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Earn4clicks
@bot.tree.command(description="Shorten your link using earn4clicks!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def earn4clicks(interaction: discord.Interaction, link: str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.req("earn4clicks", link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Gplinks
@bot.tree.command(description="Shorten your link using gplinks!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def gplinks(interaction: discord.Interaction, link: str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.req("gplinks", link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Zagl
@bot.tree.command(description="Shorten your link using zagl!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def zagl(interaction: discord.Interaction, link: str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.req("zagl", link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Isgd
@bot.tree.command(description="Shorten your link using isgd!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def isgd(interaction: discord.Interaction, link: str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.isgd.short(link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Bitly
@bot.tree.command(description="Shorten your link using bitly!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def bitly(interaction: discord.Interaction, link: str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.bitly.short(link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Chilpit
@bot.tree.command(description="Shorten your link using chilpit!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def chilpit(interaction: discord.Interaction, link: str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.chilpit.short(link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Clckru
@bot.tree.command(description="Shorten your link using clckru!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def clckru(interaction: discord.Interaction, link: str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.clckru.short(link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Cuttly
@bot.tree.command(description="Shorten your link using cuttly!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def cuttly(interaction: discord.Interaction, link: str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.cuttly.short(link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Dagd
@bot.tree.command(description="Shorten your link using dagd!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def dagd(interaction: discord.Interaction, link: str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.dagd.short(link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Osdb
@bot.tree.command(description="Shorten your link using osdb!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def osdb(interaction: discord.Interaction, link: str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.osdb.short(link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Shortcm
@bot.tree.command(description="Shorten your link using shortcm!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def shortcm(interaction: discord.Interaction, link: str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.shortcm.short(link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Tinyurl
@bot.tree.command(description="Shorten your link using tinyurl!")
@discord.app_commands.describe(link="Link you want to shorten!")
async def tinyurl(interaction: discord.Interaction, link: str):
    try:
        urlvalidator(link)
        embed = discord.Embed(
            title=shortner.tinyurl.short(link), color=0x0055FF
        ).set_footer(text="Requested By " + interaction.user.name)
        await interaction.response.send_message(embed=embed)
    except ValidationError:
        await interaction.response.send_message("Please Input A Valid Link!")


# ? Guildlist (Owner Only)
@bot.tree.command(description="Get list of servers shorty is in!")
@commands.bot_has_permissions(attach_files=True)
async def guildlist(interaction: discord.Interaction):
    check = await bot.is_owner(interaction.user)
    if check:
        with open("guildlist.csv", "w") as guild_list:
            guild_list.write("Server ID,Server Name,# of Users,Features\n")
            for guild in bot.guilds:
                # Write to csv file (guild name, total member count, region and features)
                guild_list.write(
                    f'{guild.id},"{guild.name}",{guild.member_count},{guild.features}\n'
                )
        await interaction.response.send_message(file=discord.File("guildlist.csv"))
    else:
        await interaction.response.send_message(
            "You need to be the owner of the bot to run this command!"
        )


# ? Invite
@bot.tree.command(description="Invite shorty to your server!")
async def invite(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Invite The Bot",
        description=f"[https://dsc.gg/shorty](https://dsc.gg/shorty)",
        color=0x0055FF,
    ).set_footer(text="Requested By " + interaction.user.name)
    await interaction.response.send_message(embed=embed)


# ? Support
@bot.tree.command(description="Join shorty's support server!")
async def support(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Join The Support Server",
        description=f"[https://dsc.gg/shorty-support](https://dsc.gg/shorty-support)",
        color=0x0055FF,
    ).set_footer(text="Requested By " + interaction.user.name)
    await interaction.response.send_message(embed=embed)


# ? Ping
@bot.tree.command(description="Join shorty's support server!")
async def ping(interaction: discord.Interaction):
    embed = (
        discord.Embed(color=0x0055FF)
        .add_field(name="Ping", value=bot.latency, inline=False)
        .set_footer(text="Requested By " + interaction.user.name)
    )
    await interaction.response.send_message(embed=embed)


# ? Suggest
@bot.tree.command(description="Give us your valuable suggestions!")
@discord.app_commands.describe(suggestion="Suggestion you would like to give!")
async def suggest(interaction: discord.Interaction, suggestion: str):
    embed = discord.Embed(title=suggestion, color=0x0055FF).set_author(
        name=interaction.user.name
    )
    await bot.fetch_channel(1090758793501085696).send(embed=embed)


# # ? Help
# @bot.tree.command(description="Get list of commands!")
# async def help(interaction: discord.Interaction):
#     embed = discord.Embed(
#         title="List Of Commands",
#         description="Every Command Has A Cooldown of 30 seconds!",
#         color=0x0055FF,
#     )
#     embed.add_field(name="adfly", value="Shorten Your Link Using Adfly.", inline=False)
#     embed.add_field(
#         name="nullpointer", value="Shorten Your Link Using Nullpointer.", inline=False
#     )
#     embed.add_field(name="isgd", value="Shorten Your Link Using Isgd.", inline=False)
#     embed.add_field(name="bitly", value="Shorten Your Link Using Bitly.", inline=False)
#     embed.add_field(
#         name="chilpit", value="Shorten Your Link Using Chilpit.", inline=False
#     )
#     embed.add_field(
#         name="clckru", value="Shorten Your Link Using Clckru.", inline=False
#     )
#     embed.add_field(
#         name="cuttly", value="Shorten Your Link Using Cuttly.", inline=False
#     )
#     embed.add_field(name="dagd", value="Shorten Your Link Using Dagd.", inline=False)
#     embed.add_field(name="osdb", value="Shorten Your Link Using Osdb.", inline=False)
#     embed.add_field(
#         name="shortcm", value="Shorten Your Link Using Shortcm.", inline=False
#     )
#     embed.add_field(
#         name="tinyurl", value="Shorten Your Link Using Tinyurl.", inline=False
#     )
#     embed.add_field(name="exeio", value="Shorten Your Link Using Exeio.", inline=False)
#     embed.add_field(
#         name="rebrandly", value="Shorten Your Link Using Rebrandly.", inline=False
#     )
#     embed.add_field(
#         name="gplinks", value="Shorten Your Link Using Gplinks.", inline=False
#     )
#     embed.add_field(name="zagl", value="Shorten Your Link Using Zagl.", inline=False)
#     embed.add_field(
#         name="shortest", value="Shorten Your Link Using Shortest.", inline=False
#     )
#     embed.add_field(
#         name="earn4clicks", value="Shorten Your Link Using Earn4clicks.", inline=False
#     )
#     embed.add_field(name="vurl", value="Shorten Your Link Using Vurl.", inline=False)
#     embed.add_field(
#         name="firebase",
#         value="Shorten Your Link Using Shorty's Firebase.",
#         inline=False,
#     )
#     embed.add_field(name="invite", value="Invite The Bot To Your Server", inline=False)
#     embed.add_field(
#         name="suggest",
#         value="Send A Suggestion To The Developer Of The Bot",
#         inline=False,
#     )
#     embed.add_field(
#         name="support", value="Join The Support Server Of The Bot", inline=False
#     )
#     embed.add_field(name="ping", value="Ping Of The Bot", inline=False)
#     embed.set_footer(text="Requested By " + interaction.user.name)
#     await interaction.response.send_message(embed=embed)

# ? Buy Premium
@bot.tree.command(description="Buy shorty premium!")
async def buy_premium(interaction: discord.Interaction):
    embed = (
        discord.Embed(color=0x0055FF)
        .add_field(name="Want to buy premium?", value="Join https://dsc.gg/shorty-support and create a ticket!", inline=False)
        .set_footer(text="Requested By " + interaction.user.name)
    )
    await interaction.response.send_message(embed=embed)

# ? Premium Check
@bot.tree.command(description="Check if someone has premium!")
async def check_premium(interaction: discord.Interaction, user : discord.User = None):
    if user is None:
        user = interaction.user
    else: pass
    check = await check_premium(user.id)
    if check:
        result = "You have premium!"
    else:
        result = "You don't have premium!"
    embed = (
        discord.Embed(color=0x0055FF)
        .add_field(name="Premium Check", value=result, inline=False)
        .set_footer(text="Requested By " + interaction.user.name)
    )
    await interaction.response.send_message(embed=embed)

# ? Give Premium
@bot.tree.command(description="Give someone premium! [OWNER ONLY]")
async def give_premium(interaction: discord.Interaction, user : discord.User):
    check = await bot.is_owner(interaction.user)
    if check:
        await premium_manager.add_user(user.id)
        embed = (
            discord.Embed(color=0x0055FF)
            .add_field(name="Give Premium!", value="Premium was provided to the user!", inline=False)
            .set_footer(text="Requested By " + interaction.user.name)
        )
        await interaction.response.send_message(embed=embed)
    else: await interaction.response.send_message("You need to be the owner of shorty to run this command!")

# ? Remove Premium
@bot.tree.command(description="Remove someone's premium! [OWNER ONLY]")
async def remove_premium(interaction: discord.Interaction, user : discord.User):
    check = await bot.is_owner(interaction.user)
    if check:
        await premium_manager.rm_user(user.id)
        embed = (
            discord.Embed(color=0x0055FF)
            .add_field(name="Remove Premium!", value="Premium was removed for the user!", inline=False)
            .set_footer(text="Requested By " + interaction.user.name)
        )
        await interaction.response.send_message(embed=embed)
    else: await interaction.response.send_message("You need to be the owner of shorty to run this command!")

# ? Premium list (Owner Only)
@bot.tree.command(description="Get list of all premium users! [OWNER ONLY]")
@commands.bot_has_permissions(attach_files=True)
async def premiumlist(interaction: discord.Interaction):
    check = await bot.is_owner(interaction.user)
    if check:
        with open("premiumlist.csv", "w") as guild_list:
            premium_list = await premium_manager.premium_list_gen()
            guild_list.write("Userame, Discriminator, IDs\n")
            for id in premium_list:
                user = bot.fetch_user(id)
                guild_list.write(
                    f'{user.name},"{user.discriminator}",{id}\n'
                )
        await interaction.response.send_message(file=discord.File("premiumlist.csv"))
    else:
        await interaction.response.send_message(
            "You need to be the owner of the bot to run this command!"
        )

bot.run(settings.token)
