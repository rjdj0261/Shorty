import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
from django.core.exceptions import ValidationError

load_dotenv()

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

# ? Bot class
class Shorty(commands.AutoShardedBot):
    class Settings:
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
        application_id = environ.get("APPLICATION_ID")
        shard_id = environ.get("SHARD_ID")

    class Shortners:
        """Link Shortner Class"""
        def __init__(self, settings):
            from firebase_dynamic_links import dynamic_link_builder as dlb
            import pyshorteners
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
            from requests import get, put, codes, post
            from json import dumps, loads
            if api == "exeio":
                try:
                    req = get(
                        f"https://exe.io/api?api=afe5d717ef19304362234cf6f6b3d934ab0d1a07&url={link}"
                    ).json()["shortenedUrl"]
                    return req
                except:
                    return "AN ERROR OCCURED"
            elif api == "gplinks":
                try:
                    req = get(
                        f"https://gplinks.in/api?api=eeebc0507eb61fbd079041825d73a5ddb80a7a20&url={link}"
                    ).json()["shortenedUrl"]
                    return req
                except:
                    return "AN ERROR OCCURED"
            elif api == "zagl":
                try:
                    req = get(f"").json()["shortenedUrl"]
                    return req
                except:
                    return "AN ERROR OCCURED"
            elif api == "zagl":
                try:
                    req = get(
                        f"https://za.gl/api?api=00240505bb426a55e0b1b57bcb0b02cb16d329d3&url={link}"
                    ).json()["shortenedUrl"]
                    return req
                except:
                    return "AN ERROR OCCURED"
            elif api == "earn4clicks":
                try:
                    req = get(
                        f"https://earn4clicks.in/api?api=a9fd295d6d92818d4e8db9b854ab46f167838c4f&url={link}"
                    ).json()["shortenedUrl"]
                    return req
                except:
                    return "AN ERROR OCCURED"
            elif api == "shortest":
                try:
                    req = loads(
                        put(
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
                    req = get(f"https://vurl.com/api.php?url={link}").text
                    return req
                except:
                    return "AN ERROR OCCURED"
            elif api == "rebrandly":
                linkRequest = {"destination": link, "domain": {"fullName": "rebrand.ly"}}
                requestHeaders = {
                    "Content-type": "application/json",
                    "apikey": "6053520de6be4edc9df4a55a95fc2949",
                }
                req = post(
                    "https://api.rebrandly.com/v1/links",
                    data=dumps(linkRequest),
                    headers=requestHeaders,
                )
                if req.status_code == codes.ok:
                    newurl = req.json()
                    return newurl
                else:
                    return "AN ERROR OCCURED"

    from pretty_help import PrettyHelp

    def __init__(self, intents: discord.Intents, prefix: str, help_command=PrettyHelp(color=0x0055FF, sort_commands=True)) -> None:
        super().__init__(intents=intents, command_prefix=prefix, help_command=help_command)
        from django.core.validators import URLValidator
        import platform
        from datetime import datetime
        from psutil import boot_time, cpu_freq 
        self.settings = self.Settings()
        self.activity=discord.Activity(type=discord.ActivityType.watching, name=f"/help")
        self.status=discord.Status.online
        self.shard_id=self.settings.shard_id
        self.urlvalidator = URLValidator()
        self.shortner = self.Shortners(self.settings)
        self.uname = platform.uname()
        self.boot_time_timestamp = boot_time()
        self.bt = datetime.fromtimestamp(self.boot_time_timestamp)
        self.cpufreq = cpu_freq()

# ? Commands classes
class LinkShortenerCommands(commands.Cog, name="Link Shortener Commands"):
    """Commands Used For Shortening Links"""
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.shorty: commands.AutoShardedBot = bot

    # ? Adfly
    @commands.hybrid_command(description="Shorten your link using adfly!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def adfly(self, ctx : commands.Context, link: str):
        """Shorten your links using adfly"""
        try:
            self.shorty.urlvalidator(link)
            embed = discord.discord.Embed(
                title=self.shorty.shortner.adfly.short(link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Firebase
    @commands.hybrid_command(description="Shorten your link using firebase!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def firebase(self, ctx : commands.Context, link: str):
        """Shorten your links using firebase"""
        try:
            self.shorty.urlvalidator(link)
            options = {"link": link, "apn": "com.example.android", "ibi": "com.example.ios"}
            embed = discord.discord.Embed(
                title=self.shorty.shortner.firebase.generate_short_link(
                    app_code="pocketurl", **options
                ),
                color=0x0055FF,
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Nullpointer
    @commands.hybrid_command(description="Shorten your link using nullpointer!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def nullpointer(self, ctx : commands.Context, link: str):
        """Shorten your links using nullpointer"""
        try:
            self.shorty.urlvalidator(link)
            embed = discord.Embed(
                title=self.shorty.shortner.nullpointer.short(link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Exeio
    @commands.hybrid_command(description="Shorten your link using exeio!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def exeio(self, ctx : commands.Context, link: str):
        """Shorten your links using exeio"""
        try:
            self.shorty.urlvalidator(link)
            embed = discord.Embed(
                title=self.shorty.shortner.req("exeio", link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Vurl
    @commands.hybrid_command(description="Shorten your link using vurl!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def vurl(self, ctx : commands.Context, link: str):
        """Shorten your links using vurl"""
        try:
            self.shorty.urlvalidator(link)
            embed = discord.Embed(
                title=self.shorty.shortner.req("vurl", link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Rebrandly
    @commands.hybrid_command(description="Shorten your link using rebrandly!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def rebrandly(self, ctx : commands.Context, link: str):
        """Shorten your links using rebrandly"""
        try:
            self.shorty.urlvalidator(link)
            embed = discord.Embed(
                title=self.shorty.shortner.req("rebrandly", link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Shortest
    @commands.hybrid_command(description="Shorten your link using shortest!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def shortest(self, ctx : commands.Context, link: str):
        """Shorten your links using shortest"""
        try:
            self.shorty.urlvalidator(link)
            embed = discord.Embed(
                title=self.shorty.shortner.req("shortest", link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Earn4clicks
    @commands.hybrid_command(description="Shorten your link using earn4clicks!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def earn4clicks(self, ctx : commands.Context, link: str):
        """Shorten your links using earn4clicks"""
        try:
            self.shorty.urlvalidator(link)
            embed = discord.Embed(
                title=self.shorty.shortner.req("earn4clicks", link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Gplinks
    @commands.hybrid_command(description="Shorten your link using gplinks!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def gplinks(self, ctx : commands.Context, link: str):
        """Shorten your links using gplinks"""
        try:
            self.shorty.urlvalidator(link)
            embed = discord.Embed(
                title=self.shorty.shortner.req("gplinks", link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Zagl
    @commands.hybrid_command(description="Shorten your link using zagl!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def zagl(self, ctx : commands.Context, link: str):
        """Shorten your links using zagl"""
        try:
            self.shorty.urlvalidator(link)
            embed = discord.Embed(
                title=self.shorty.shortner.req("zagl", link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Isgd
    @commands.hybrid_command(description="Shorten your link using isgd!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def isgd(self, ctx : commands.Context, link: str):
        """Shorten your links using isgd"""
        try:
            self.shorty.urlvalidator(link)
            embed = discord.Embed(
                title=self.shorty.shortner.isgd.short(link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Bitly
    @commands.hybrid_command(description="Shorten your link using bitly!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def bitly(self, ctx : commands.Context, link: str):
        """Shorten your links using bitly"""
        try:
            self.shorty.urlvalidator(link)
            embed = discord.Embed(
                title=self.shorty.shortner.bitly.short(link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Chilpit
    @commands.hybrid_command(description="Shorten your link using chilpit!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def chilpit(self, ctx : commands.Context, link: str):
        """Shorten your links using chilpit"""
        try:
            self.shorty.urlvalidator(link)
            embed = discord.Embed(
                title=self.shorty.shortner.chilpit.short(link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Clckru
    @commands.hybrid_command(description="Shorten your link using clckru!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def clckru(self, ctx : commands.Context, link: str):
        """Shorten your links using clckru"""
        try:
            self.shorty.urlvalidator(link)
            embed = discord.Embed(
                title=self.shorty.shortner.clckru.short(link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Cuttly
    @commands.hybrid_command(description="Shorten your link using cuttly!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def cuttly(self, ctx : commands.Context, link: str):
        """Shorten your links using cuttly"""
        try:
            self.shorty.urlvalidator(link)
            embed = discord.Embed(
                title=self.shorty.shortner.cuttly.short(link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Dagd
    @commands.hybrid_command(description="Shorten your link using dagd!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def dagd(self, ctx : commands.Context, link: str):
        """Shorten your links using dagd"""
        try:
            self.shorty.urlvalidator(link)
            embed = discord.Embed(
                title=self.shorty.shortner.dagd.short(link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Osdb
    @commands.hybrid_command(description="Shorten your link using osdb!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def osdb(self, ctx : commands.Context, link: str):
        """Shorten your links using osdb"""
        try:
            self.shorty.urlvalidator(link)
            embed = discord.Embed(
                title=self.shorty.shortner.osdb.short(link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Shortcm
    @commands.hybrid_command(description="Shorten your link using shortcm!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def shortcm(self, ctx : commands.Context, link: str):
        """Shorten your links using shortcm"""
        try:
            self.shorty.urlvalidator(link)
            embed = discord.Embed(
                title=self.shorty.shortner.shortcm.short(link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Tinyurl
    @commands.hybrid_command(description="Shorten your link using tinyurl!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def tinyurl(self, ctx : commands.Context, link: str):
        """Shorten your links using tinyurl"""
        try:
            self.shorty.urlvalidator(link)
            embed = discord.Embed(
                title=self.shorty.shortner.tinyurl.short(link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")

class EventListeners(commands.Cog, name="Event Listeners"):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.shorty: commands.AutoShardedBot = bot

    # ? On Ready Event
    @commands.Cog.listener()
    async def on_ready(self):
        from psutil import  cpu_count, cpu_percent, virtual_memory
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
        print(f"System: {self.shorty.uname.system}")
        print(f"Node Name: {self.shorty.uname.node}")
        print(f"Release: {self.shorty.uname.release}")
        print(f"Version: {self.shorty.uname.version}")
        print(f"Machine: {self.shorty.uname.machine}")
        print(f"Processor: {self.shorty.uname.processor}")
        print("=" * 40, "Boot Time", "=" * 40)
        print(f"Boot Time: {self.shorty.bt.year}/{self.shorty.bt.month}/{self.shorty.bt.day} {self.shorty.bt.hour}:{self.shorty.bt.minute}:{self.shorty.bt.second}")
        # let's print CPU information
        print("=" * 40, "CPU Info", "=" * 40)
        # number of cores
        print("Physical cores:", cpu_count(logical=False))
        print("Total cores:", cpu_count(logical=True))
        # CPU frequencies
        print(f"Max Frequency: {self.shorty.cpufreq.max:.2f}Mhz")
        print(f"Min Frequency: {self.shorty.cpufreq.min:.2f}Mhz")
        print(f"Current Frequency: {self.shorty.cpufreq.current:.2f}Mhz")
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
        logger.warning("We have logged in as {0.user}".format(shorty))

    # ? Command Error Handler
    @commands.Cog.listener()
    async def on_command_error(self, ctx : commands.Context, error: commands.CommandError):
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
            await self.shorty.get_channel(1090745096040894604).send(error)
            logger.error(error)

        await ctx.send(message, delete_after=5)

class UtilityCommands(commands.Cog, name="Utility Commands"):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.shorty: commands.AutoShardedBot = bot

    # ? Invite
    @commands.hybrid_command(description="Invite shorty to your server!")
    async def invite(self, ctx : commands.Context):
        """"Get the link to invite the bot"""
        embed = discord.Embed(
            title="Invite The Bot",
            description=f"[https://dsc.gg/shorty](https://dsc.gg/shorty)",
            color=0x0055FF,
        ).set_footer(text="Requested By " + ctx.author.name)
        await ctx.send(embed=embed)


    # ? Support
    @commands.hybrid_command(description="Join shorty's support server!")
    async def support(self, ctx : commands.Context):
        """Get the link to the support server"""
        embed = discord.Embed(
            title="Join The Support Server",
            description=f"[https://dsc.gg/shorty-support](https://dsc.gg/shorty-support)",
            color=0x0055FF,
        ).set_footer(text="Requested By " + ctx.author.name)
        await ctx.send(embed=embed)


    # ? Ping
    @commands.hybrid_command(description="Join shorty's support server!")
    async def ping(self, ctx : commands.Context):
        """Get the bot's ping"""
        embed = (
            discord.Embed(color=0x0055FF)
            .add_field(name="Ping", value=shorty.latency, inline=False)
            .set_footer(text="Requested By " + ctx.author.name)
        )
        await ctx.send(embed=embed)


    # ? Suggest
    @commands.hybrid_command(description="Give us your valuable suggestions!")
    @discord.app_commands.describe(suggestion="Suggestion you would like to give!")
    async def suggest(self, ctx : commands.Context, suggestion: str):
        """Give suggestions"""
        embed = discord.Embed(title=suggestion, color=0x0055FF).set_author(
            name=ctx.author.name
        )
        await shorty.fetch_channel(1090758793501085696).send(embed=embed)

class OwnerCommands(commands.Cog, name="Owner Only Commands"):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.shorty: commands.AutoShardedBot = bot

    # ? Sync
    @commands.hybrid_command(description="Sync Command Updates.")
    async def sync(self, ctx : commands.Context):
        """Sync command updates"""
        check = await shorty.is_owner(ctx.author)
        if check:
            await shorty.tree.sync()
        else: await ctx.send("You need to be the owner of shorty to run this command!")
    
    # ? Guildlist
    @commands.hybrid_command(description="Get List Of Guilds The Bot Is In.")
    async def guildlist(self, ctx : commands.Context):
        """Get list of all the guilds the bot is in"""
        check = await shorty.is_owner(ctx.author)
        if check:
            with open("guildlist.csv", "w") as guild_list:
                guild_list.write("Server ID,Server Name,# of Users,Features\n")
                for guild in shorty.guilds:
                    # Write to csv file (guild name, total member count, region and features)
                    guild_list.write(
                        f'{guild.id},"{guild.name}",{guild.member_count},{guild.features}\n'
                    )
            await ctx.send(file=discord.File("guildlist.csv"))
        else:
            await ctx.send(
                "You need to be the owner of the bot to run this command!"
            )

# ? Bot Init
intents = discord.Intents.default()
intents.message_content = True
prefix = "!"
shorty = Shorty(intents=intents, prefix=prefix)

# ? Initiate Sentry
from sentry_sdk import init as sentry_init
sentry_init(
    dsn=shorty.settings.sentry,
    traces_sample_rate=1.0,
    release="shorty@1.0.0",
    sample_rate=0.25,
    _experiments={"profiles_sample_rate": 1.0},
    environment="staging",
    max_breadcrumbs=50,
)

# ? Initiate Logger
logger = logging.getLogger(__name__)

# ? Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler(shorty.settings.log_file)
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

# ? Load Commands
async def load():
    await shorty.add_cog(LinkShortenerCommands(shorty))
    await shorty.add_cog(EventListeners(shorty))
    await shorty.add_cog(UtilityCommands(shorty))
    await shorty.add_cog(OwnerCommands(shorty))
from asyncio import run
run(load())

shorty.run(shorty.settings.token)
