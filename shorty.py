import discord
from discord import app_commands
from sentry_sdk import init as sentry_init
from discord.ext import commands
from psutil import boot_time, cpu_count, cpu_freq, cpu_percent, virtual_memory
import logging
import platform
from datetime import datetime
from django.core.exceptions import ValidationError
from django.core.validators import URLvalidator
import pyshorteners
from firebase_dynamic_links import dynamic_link_builder as dlb
import requests
from json import dumps, loads
from aioredis import from_url
from dotenv import load_dotenv
from asyncio import run

load_dotenv()

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
        prefix = environ.get("PREFIX")
        redis_url = environ.get("REDIS_URL")
        application_id = environ.get("APPLICATION_ID")
        shard_id = environ.get("SHARD_ID")

    class Shortners:
        """Link Shortner Class"""
        def __init__(self, settings):
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

    class Premium_Manager:
        """A class that manages premium users"""
        def __init__(self, redis) -> None:
            self.redis = redis
        async def premium_list_update(self, premium_list : list):
            """Updates premium list after changes

            Args:
                premium_list (list): list of premium ids
            """
            premium_str = ""
            for i in premium_list:
                premium_str += (i + " ")
            await self.redis.set("premium", premium_str)

        async def premium_list_gen(self):
            """Generates Premium List and returns it.

            Returns:
                premium_list: list containing premium ids
            """
            premium_str = await self.redis.get("premium")
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

    def __init__(self) -> None:
        self.redis = from_url(self.settings.redis_url)
        self.settings = self.Settings()
        self.premium_manager = self.Premium_Manager(self.redis)
        self.command_prefix=self.settings.prefix,
        self.intents_settings=discord.Intents.default()
        self.intents_settings.message_content = True,
        self.intents=self.intents_settings
        self.help_command=None,
        self.activity=discord.Activity(type=discord.ActivityType.watching, name=f"/help")
        self.status=discord.Status.online
        self.application_id=self.settings.application_id
        self.command_prefix=self.settings.prefix
        self.shard_id=self.settings.shard_id
        self.urlvalidator = URLvalidator()
        self.shortner = self.Shortners(self.settings)
        self.uname = platform.uname()
        self.boot_time_timestamp = boot_time()
        self.bt = datetime.fromtimestamp(self.boot_time_timestamp)
        self.cpufreq = cpu_freq()

# ? Commands class
class Commands(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.shorty: commands.AutoShardedBot = bot

    # ? On Ready Event
    @commands.Cog.listener()
    async def on_ready(self):
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
        print(f"Total: {self.shorty.get_size(svmem.total)}")
        print(f"Available: {self.shorty.get_size(svmem.available)}")
        print(f"Used: {self.shorty.get_size(svmem.used)}")
        print(f"Percentage: {svmem.percent}%")
        print("=" * 40, "Logs", "=" * 40)
        logger.warning("We have logged in as {0.user}".format(shorty))

    # ? Command Error Handler
    @commands.Cog.listener()
    async def on_command_error(self, ctx : discord.Context, error: commands.CommandError):
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

    # ? Adfly
    @commands.hybrid_command(description="Shorten your link using adfly!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def adfly(self, ctx : discord.Context, link: str):
        try:
            shorty.urlvalidator(link)
            embed = discord.discord.Embed(
                title=shorty.shortner.adfly.short(link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Firebase
    @commands.hybrid_command(description="Shorten your link using firebase!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def firebase(self, ctx : discord.Context, link: str):
        try:
            shorty.urlvalidator(link)
            options = {"link": link, "apn": "com.example.android", "ibi": "com.example.ios"}
            embed = discord.discord.Embed(
                title=shorty.shortner.firebase.generate_short_link(
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
    async def nullpointer(self, ctx : discord.Context, link: str):
        try:
            shorty.urlvalidator(link)
            embed = discord.Embed(
                title=shorty.shortner.nullpointer.short(link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Exeio
    @commands.hybrid_command(description="Shorten your link using exeio!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def exeio(self, ctx : discord.Context, link: str):
        try:
            shorty.urlvalidator(link)
            embed = discord.Embed(
                title=shorty.shortner.req("exeio", link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Vurl
    @commands.hybrid_command(description="Shorten your link using vurl!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def vurl(self, ctx : discord.Context, link: str):
        try:
            shorty.urlvalidator(link)
            embed = discord.Embed(
                title=shorty.shortner.req("vurl", link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Rebrandly
    @commands.hybrid_command(description="Shorten your link using rebrandly!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def rebrandly(self, ctx : discord.Context, link: str):
        try:
            shorty.urlvalidator(link)
            embed = discord.Embed(
                title=shorty.shortner.req("rebrandly", link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Shortest
    @commands.hybrid_command(description="Shorten your link using shortest!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def shortest(self, ctx : discord.Context, link: str):
        try:
            shorty.urlvalidator(link)
            embed = discord.Embed(
                title=shorty.shortner.req("shortest", link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Earn4clicks
    @commands.hybrid_command(description="Shorten your link using earn4clicks!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def earn4clicks(self, ctx : discord.Context, link: str):
        try:
            shorty.urlvalidator(link)
            embed = discord.Embed(
                title=shorty.shortner.req("earn4clicks", link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Gplinks
    @commands.hybrid_command(description="Shorten your link using gplinks!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def gplinks(self, ctx : discord.Context, link: str):
        try:
            shorty.urlvalidator(link)
            embed = discord.Embed(
                title=shorty.shortner.req("gplinks", link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Zagl
    @commands.hybrid_command(description="Shorten your link using zagl!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def zagl(self, ctx : discord.Context, link: str):
        try:
            shorty.urlvalidator(link)
            embed = discord.Embed(
                title=shorty.shortner.req("zagl", link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Isgd
    @commands.hybrid_command(description="Shorten your link using isgd!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def isgd(self, ctx : discord.Context, link: str):
        try:
            shorty.urlvalidator(link)
            embed = discord.Embed(
                title=shorty.shortner.isgd.short(link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Bitly
    @commands.hybrid_command(description="Shorten your link using bitly!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def bitly(self, ctx : discord.Context, link: str):
        try:
            shorty.urlvalidator(link)
            embed = discord.Embed(
                title=shorty.shortner.bitly.short(link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Chilpit
    @commands.hybrid_command(description="Shorten your link using chilpit!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def chilpit(self, ctx : discord.Context, link: str):
        try:
            shorty.urlvalidator(link)
            embed = discord.Embed(
                title=shorty.shortner.chilpit.short(link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Clckru
    @commands.hybrid_command(description="Shorten your link using clckru!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def clckru(self, ctx : discord.Context, link: str):
        try:
            shorty.urlvalidator(link)
            embed = discord.Embed(
                title=shorty.shortner.clckru.short(link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Cuttly
    @commands.hybrid_command(description="Shorten your link using cuttly!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def cuttly(self, ctx : discord.Context, link: str):
        try:
            shorty.urlvalidator(link)
            embed = discord.Embed(
                title=shorty.shortner.cuttly.short(link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Dagd
    @commands.hybrid_command(description="Shorten your link using dagd!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def dagd(self, ctx : discord.Context, link: str):
        try:
            shorty.urlvalidator(link)
            embed = discord.Embed(
                title=shorty.shortner.dagd.short(link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Osdb
    @commands.hybrid_command(description="Shorten your link using osdb!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def osdb(self, ctx : discord.Context, link: str):
        try:
            shorty.urlvalidator(link)
            embed = discord.Embed(
                title=shorty.shortner.osdb.short(link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Shortcm
    @commands.hybrid_command(description="Shorten your link using shortcm!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def shortcm(self, ctx : discord.Context, link: str):
        try:
            shorty.urlvalidator(link)
            embed = discord.Embed(
                title=shorty.shortner.shortcm.short(link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Tinyurl
    @commands.hybrid_command(description="Shorten your link using tinyurl!")
    @discord.app_commands.describe(link="Link you want to shorten!")
    async def tinyurl(self, ctx : discord.Context, link: str):
        try:
            shorty.urlvalidator(link)
            embed = discord.Embed(
                title=shorty.shortner.tinyurl.short(link), color=0x0055FF
            ).set_footer(text="Requested By " + ctx.author.name)
            await ctx.send(embed=embed)
        except ValidationError:
            await ctx.send("Please Input A Valid Link!")


    # ? Guildlist (Owner Only)
    @commands.hybrid_command(description="Get list of servers shorty is in!")
    @commands.bot_has_permissions(attach_files=True)
    async def guildlist(self, ctx : discord.Context):
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


    # ? Invite
    @commands.hybrid_command(description="Invite shorty to your server!")
    async def invite(self, ctx : discord.Context):
        embed = discord.Embed(
            title="Invite The Bot",
            description=f"[https://dsc.gg/shorty](https://dsc.gg/shorty)",
            color=0x0055FF,
        ).set_footer(text="Requested By " + ctx.author.name)
        await ctx.send(embed=embed)


    # ? Support
    @commands.hybrid_command(description="Join shorty's support server!")
    async def support(self, ctx : discord.Context):
        embed = discord.Embed(
            title="Join The Support Server",
            description=f"[https://dsc.gg/shorty-support](https://dsc.gg/shorty-support)",
            color=0x0055FF,
        ).set_footer(text="Requested By " + ctx.author.name)
        await ctx.send(embed=embed)


    # ? Ping
    @commands.hybrid_command(description="Join shorty's support server!")
    async def ping(self, ctx : discord.Context):
        embed = (
            discord.Embed(color=0x0055FF)
            .add_field(name="Ping", value=shorty.latency, inline=False)
            .set_footer(text="Requested By " + ctx.author.name)
        )
        await ctx.send(embed=embed)


    # ? Suggest
    @commands.hybrid_command(description="Give us your valuable suggestions!")
    @discord.app_commands.describe(suggestion="Suggestion you would like to give!")
    async def suggest(self, ctx : discord.Context, suggestion: str):
        embed = discord.Embed(title=suggestion, color=0x0055FF).set_author(
            name=ctx.author.name
        )
        await shorty.fetch_channel(1090758793501085696).send(embed=embed)


    # ? Help
    @commands.hybrid_command(description="Get list of commands!")
    async def help(self, ctx : discord.Context):
        embed = discord.Embed(
            title="List Of Commands",
            description="Every Command Has A Cooldown of 30 seconds!",
            color=0x0055FF,
        )
        embed.add_field(name="adfly", value="Shorten Your Link Using Adfly.", inline=False)
        embed.add_field(
            name="nullpointer", value="Shorten Your Link Using Nullpointer.", inline=False
        )
        embed.add_field(name="isgd", value="Shorten Your Link Using Isgd.", inline=False)
        embed.add_field(name="bitly", value="Shorten Your Link Using Bitly.", inline=False)
        embed.add_field(
            name="chilpit", value="Shorten Your Link Using Chilpit.", inline=False
        )
        embed.add_field(
            name="clckru", value="Shorten Your Link Using Clckru.", inline=False
        )
        embed.add_field(
            name="cuttly", value="Shorten Your Link Using Cuttly.", inline=False
        )
        embed.add_field(name="dagd", value="Shorten Your Link Using Dagd.", inline=False)
        embed.add_field(name="osdb", value="Shorten Your Link Using Osdb.", inline=False)
        embed.add_field(
            name="shortcm", value="Shorten Your Link Using Shortcm.", inline=False
        )
        embed.add_field(
            name="tinyurl", value="Shorten Your Link Using Tinyurl.", inline=False
        )
        embed.add_field(name="exeio", value="Shorten Your Link Using Exeio.", inline=False)
        embed.add_field(
            name="rebrandly", value="Shorten Your Link Using Rebrandly.", inline=False
        )
        embed.add_field(
            name="gplinks", value="Shorten Your Link Using Gplinks.", inline=False
        )
        embed.add_field(name="zagl", value="Shorten Your Link Using Zagl.", inline=False)
        embed.add_field(
            name="shortest", value="Shorten Your Link Using Shortest.", inline=False
        )
        embed.add_field(
            name="earn4clicks", value="Shorten Your Link Using Earn4clicks.", inline=False
        )
        embed.add_field(name="vurl", value="Shorten Your Link Using Vurl.", inline=False)
        embed.add_field(
            name="firebase", value="Shorten Your Link Using Shorty's Firebase.", inline=False,
        )
        embed.add_field(name="invite", value="Invite The Bot To Your Server", inline=False)
        embed.add_field(
            name="suggest", value="Send A Suggestion To The Developer Of The Bot", inline=False,
        )
        embed.add_field(
            name="support", value="Join The Support Server Of The Bot", inline=False
        )
        embed.add_field(name="ping", value="Ping Of The Bot", inline=False)
        embed.add_field(name="check_premium", value="Check If Someone Has Premium", inline=False)
        embed.add_field(name="give_premium", value="Give Someone Premium (Owner Only)", inline=False)
        embed.add_field(name="remove_premium", value="Remove Someone's Premium (Owner Only)", inline=False)
        embed.add_field(name="premiumlist", value="Get A List Of Users Having Premium (Owner Only)", inline=False)
        embed.set_footer(text="Requested By " + ctx.author.name)
        await ctx.send(embed=embed)

    # ? Buy Premium
    @commands.hybrid_command(description="Buy shorty premium!")
    async def buy_premium(self, ctx : discord.Context):
        embed = (
            discord.Embed(color=0x0055FF)
            .add_field(name="Want to buy premium?", value="Join https://dsc.gg/shorty-support and create a ticket!", inline=False)
            .set_footer(text="Requested By " + ctx.author.name)
        )
        await ctx.send(embed=embed)

    # ? Premium Check
    @commands.hybrid_command(description="Check if someone has premium!")
    async def check_premium(self, ctx : discord.Context, user : discord.User = None):
        if user is None:
            user = ctx.author
        else: pass
        check = await shorty.premium_manager.premium_check(user.id)
        if check:
            result = "You have premium!"
        else:
            result = "You don't have premium!"
        embed = (
            discord.Embed(color=0x0055FF)
            .add_field(name="Premium Check", value=result, inline=False)
            .set_footer(text="Requested By " + ctx.author.name)
        )
        await ctx.send(embed=embed)

    # ? Give Premium
    @commands.hybrid_command(description="Give someone premium! [OWNER ONLY]")
    async def give_premium(self, ctx : discord.Context, user : discord.User):
        check = await shorty.is_owner(ctx.author)
        if check:
            await shorty.premium_manager.add_user(user.id)
            embed = (
                discord.Embed(color=0x0055FF)
                .add_field(name="Give Premium!", value="Premium was provided to the user!", inline=False)
                .set_footer(text="Requested By " + ctx.author.name)
            )
            await ctx.send(embed=embed)
        else: await ctx.send("You need to be the owner of shorty to run this command!")

    # ? Remove Premium (Owner Only) 
    @commands.hybrid_command(description="Remove someone's premium! [OWNER ONLY]")
    async def remove_premium(self, ctx : discord.Context, user : discord.User):
        check = await shorty.is_owner(ctx.author)
        if check:
            await shorty.premium_manager.rm_user(user.id)
            embed = (
                discord.Embed(color=0x0055FF)
                .add_field(name="Remove Premium!", value="Premium was removed for the user!", inline=False)
                .set_footer(text="Requested By " + ctx.author.name)
            )
            await ctx.send(embed=embed)
        else: await ctx.send("You need to be the owner of shorty to run this command!")

    # ? Premium list (Owner Only)
    @commands.hybrid_command(description="Get list of all premium users! [OWNER ONLY]")
    @commands.bot_has_permissions(attach_files=True)
    async def premiumlist(self, ctx : discord.Context):
        check = await shorty.is_owner(ctx.author)
        if check:
            with open("premiumlist.csv", "w") as guild_list:
                premium_list = await shorty.premium_manager.premium_list_gen()
                guild_list.write("Userame, Discriminator, IDs\n")
                for id in premium_list:
                    user = shorty.fetch_user(id)
                    guild_list.write(
                        f'{user.name},"{user.discriminator}",{id}\n'
                    )
            await ctx.send(file=discord.File("premiumlist.csv"))
        else:
            await ctx.send(
                "You need to be the owner of the bot to run this command!"
            )

    # ? Sync
    @commands.hybrid_command()
    async def sync(self, ctx : discord.Context):
        check = await shorty.is_owner(ctx.author)
        if check:
            await shorty.tree.sync()
        else: await ctx.send("You need to be the owner of shorty to run this command!")

    @commands.hybrid_command(name="ping")
    async def ping_command(self, ctx: commands.Context) -> None:
        await ctx.send("Hello!")

# ? Bot Init
shorty = Shorty()

# ? Initiate Sentry
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

async def start():
    await shorty.add_cog(Commands(shorty))
    shorty.run(shorty.settings.token)

run(start())
