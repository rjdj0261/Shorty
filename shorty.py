#!/usr/bin/env python3

# ? Imports

import logging
import os
import platform
from asyncio import sleep as _sleep
from datetime import datetime
from traceback import format_exc
import aiohttp
import discord
import psutil
import pyshorteners
import sentry_sdk
import statcord
from discord import Embed
from discord.ext import commands
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from firebase_dynamic_links import dynamic_link_builder
import requests
import json


# ? Initiate Sentry

sentry_sdk.init(
    "https://5a2f4314d5e64816871afc04b5237c13@o574256.ingest.sentry.io/5744939",
    traces_sample_rate=1.0,
    release="shorty@1.0.0",
    sample_rate=0.25
)

# ? Shorten The Output Of Bytes


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


# ? Shortener Creator Class

class shortners:
    def __init__(self):
        self.isgd = pyshorteners.Shortener().isgd
        self.nullpointer = pyshorteners.Shortener(
            domain="https://0x0.st").nullpointer
        self.bitly = pyshorteners.Shortener(
            api_key="eabb226f5855deb8fe02998123605a439f47d9b4").bitly
        self.chilpit = pyshorteners.Shortener().chilpit
        self.clckru = pyshorteners.Shortener().clckru
        self.cuttly = pyshorteners.Shortener(
            api_key="b82be139ae1d0c408a1f44d31b48dc4f5cebf").cuttly
        self.dagd = pyshorteners.Shortener().dagd
        self.osdb = pyshorteners.Shortener().osdb
        self.shortcm = pyshorteners.Shortener(
            api_key="0b36dd07-d05da0b5-67052811-e4e65108", domain="3adu.short.gy"
        ).shortcm
        self.tinyurl = pyshorteners.Shortener().tinyurl
        self.adfly = pyshorteners.Shortener(
            api_key="d29be96973c37752a43f1f26e1f79d08",
            user_id="24827485",
            domain="test.us",
            group_id=12,
            type="int",
        )
        self.firebase = dynamic_link_builder(
            api_key="AIzaSyDsi_Uumfc_Fvkjd0MC7JM01o-otzzTeRg")

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
                newurl = r.json()
                return newurl
            else:
                return "AN ERROR OCCURED"


# ? Initiate Bot
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("?"),
    help_command=None,
)

# ? Initate URLValidator
urlvalidator = URLValidator()

# ? Initiate Shorteners
shortner = shortners()

# ? Initiate Statcord
statcord_key = "statcord.com-l6MDyFBxKPRCJESE2DTm"
api = statcord.Client(bot, statcord_key)
api.start_loop()

# ? Initiate Logger
logger = logging.getLogger(__name__)

# ? Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler("bot.log")
c_handler.setLevel(logging.WARNING)
f_handler.setLevel(logging.ERROR)

# ? Create formatters and add it to handlers
c_format = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
f_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# ? Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)


# ? Error Handler

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        return  # Return because we don't want to show an error for every command not found
    elif isinstance(error, commands.CommandOnCooldown):
        message = f"This command is on cooldown. Please try again after {round(error.retry_after, 1)} seconds."
    elif isinstance(error, commands.MissingPermissions):
        message = "You are missing the required permissions to run this command!"
    elif isinstance(error, commands.UserInputError):
        message = f"Something about your input was wrong, please ensure the you use ```?command (link)``` check your input and try again!"
    elif isinstance(error, commands.NotOwner):
        return
    else:
        message = "Oh no! Something went wrong while running the command!"
        await bot.get_channel(940164006998589470).send(error)
        logger.error(error)

    await ctx.send(message, delete_after=5)
    await ctx.message.delete(delay=5)


# ? Discord.py Ready Event

@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"?help in {len(bot.guilds)} servers!",
        )
    )
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
    bt = datetime.fromtimestamp(boot_time_timestamp)
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


# ? Discord.py Guild Join Event

@bot.event
async def on_guild_join(guild):
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"?help in {len(bot.guilds)} servers!",
        )
    )


# ? Discord.py Guild Remove Event

@bot.event
async def on_guild_remove(guild):
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"?help in {len(bot.guilds)} servers!",
        )
    )


# ? Discord.py on_command Event For Statcord.py

@bot.event
async def on_command(ctx):
    api.command_run(ctx)


# ? Adfly Command

@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def adfly(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(title=shortner.adfly.short(link), color=0x0055FF).set_footer(
            text="Requested By " + ctx.author.name
        )
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


# ? Firebase Command

@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def firebase(ctx, link):
    try:
        urlvalidator(link)
        options = {
            'link': link,
            'apn': 'com.example.android',
            'ibi': 'com.example.ios'
        }
        embed = Embed(title=shortner.firebase.generate_short_link(app_code='pocketurl', **options), color=0x0055FF).set_footer(
            text="Requested By " + ctx.author.name
        )
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


# ? Nullpointer Command

@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def nullpointer(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(
            title=shortner.nullpointer.short(link), color=0x0055FF
        ).set_footer(text="Requested By " + ctx.author.name)
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


# ? Exeio Command

@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def exeio(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(
            title=shortner.req("exeio", link), color=0x0055FF
        ).set_footer(text="Requested By " + ctx.author.name)
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


# ? Vurl Command

@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def vurl(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(
            title=shortner.req("vurl", link), color=0x0055FF
        ).set_footer(text="Requested By " + ctx.author.name)
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


# ? Rebrandly Command

@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def rebrandly(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(
            title=shortner.req("rebrandly", link), color=0x0055FF
        ).set_footer(text="Requested By " + ctx.author.name)
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


# ? Shortest Command

@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def shortest(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(
            title=shortner.req("shortest", link), color=0x0055FF
        ).set_footer(text="Requested By " + ctx.author.name)
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


# ? Earn4clicks Command

@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def earn4clicks(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(
            title=shortner.req("earn4clicks", link), color=0x0055FF
        ).set_footer(text="Requested By " + ctx.author.name)
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


# ? Gplinks Command

@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def gplinks(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(
            title=shortner.req("gplinks", link), color=0x0055FF
        ).set_footer(text="Requested By " + ctx.author.name)
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


# ? Zagl Command

@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def zagl(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(
            title=shortner.req("zagl", link), color=0x0055FF
        ).set_footer(text="Requested By " + ctx.author.name)
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


# ? Isgd Command

@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def isgd(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(title=shortner.isgd.short(link), color=0x0055FF).set_footer(
            text="Requested By " + ctx.author.name
        )
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


# ? Bitly Command

@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def bitly(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(title=shortner.bitly.short(link), color=0x0055FF).set_footer(
            text="Requested By " + ctx.author.name
        )
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


# ? Chilpit Command

@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def chilpit(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(title=shortner.chilpit.short(link), color=0x0055FF).set_footer(
            text="Requested By " + ctx.author.name
        )
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


# ? Clckru Command

@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def clckru(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(title=shortner.clckru.short(link), color=0x0055FF).set_footer(
            text="Requested By " + ctx.author.name
        )
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


# ? Cuttly Command

@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def cuttly(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(title=shortner.cuttly.short(link), color=0x0055FF).set_footer(
            text="Requested By " + ctx.author.name
        )
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


# ? Dagd Command

@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def dagd(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(title=shortner.dagd.short(link), color=0x0055FF).set_footer(
            text="Requested By " + ctx.author.name
        )
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


# ? Osdb Command

@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def osdb(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(title=shortner.osdb.short(link), color=0x0055FF).set_footer(
            text="Requested By " + ctx.author.name
        )
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


# ? Shortcm Command

@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def shortcm(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(title=shortner.shortcm.short(link), color=0x0055FF).set_footer(
            text="Requested By " + ctx.author.name
        )
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


# ? Tinyurl Command

@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def tinyurl(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(title=shortner.tinyurl.short(link), color=0x0055FF).set_footer(
            text="Requested By " + ctx.author.name
        )
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


# ? Invite Command

@bot.command()
async def invite(ctx):
    embed = Embed(
        title="Invite The Bot",
        description=f"[https://dsc.gg/shorty](https://dsc.gg/shorty)",
        color=0x0055FF,
    ).set_footer(text="Requested By " + ctx.author.name)
    await ctx.send(embed=embed)


# ? Support Command

@bot.command()
async def support(ctx):
    embed = Embed(
        title="Join The Support Server",
        description=f'[https://dsc.gg/shorty-support](https://dsc.gg/shorty-support)',
        color=0x0055FF,
    ).set_footer(text="Requested By " + ctx.author.name)
    await ctx.send(embed=embed)


# ? Ping Command

@bot.command()
async def ping(ctx):
    embed = (
        Embed(color=0x0055FF)
        .add_field(name="Ping", value=bot.latency, inline=False)
        .set_footer(text="Requested By " + ctx.author.name)
    )
    await ctx.send(embed=embed)


# ? Help Command

@bot.command()
async def help(ctx):
    embed = Embed(
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
        name="support", value="Join The Support Server Of The Bot", inline=False
    )
    embed.add_field(
        name="ping", value="Ping Of The Bot", inline=False
    )
    embed.set_footer(
        text="Requested By " + ctx.author.name
    )

    await ctx.send(embed=embed)


# ? Eval Command (Owner Only)

@bot.command(name="eval", hidden=True)
@commands.is_owner()
async def eval_(ctx: commands.Context, *, code: str):
    code = code.strip("`")
    if code.startswith(("py\n", "python\n")):
        code = "\n".join(code.split("\n")[1:])

    try:
        exec(
            "async def __function():\n"
            + "".join(f"\n    {line}" for line in code.split("\n")),
            locals(),
        )

        await locals()["__function"]()
    except:
        await ctx.send(
            embed=Embed(
                title="Error!",
                description=f"```{format_exc()}```",
                color=discord.Color.red(),
            ).set_footer(
                text=f"Invoker: {ctx.author}",
                icon_url=ctx.author.avatar_url_as(format="png"),
            )
        )


# ? Eval Error Handler

@eval_.error
async def eval__error(ctx, error):
    await ctx.send(
        embed=Embed(
            title="Error!", description=f"```{error}```", color=discord.Color.red()
        ).set_footer(
            text=f"Invoker: {ctx.author}",
            icon_url=ctx.author.avatar_url_as(format="png"),
        )
    )


# ? Selfpurge Command (Owner Only)

@bot.command(hidden=True)
@commands.is_owner()
async def selfpurge(ctx, amount=2):
    amount = int(amount)

    def fusion(m):
        return bot.user.id == m.author.id

    await ctx.message.channel.purge(limit=amount, check=fusion, bulk=False)
    await ctx.send(
        embed=Embed(
            title="Purged",
            description=f"{ctx.author.mention} i have successfully purged `{amount}` of messages in <#{ctx.message.channel.id}>",
            color=ctx.author.color,
        ),
        delete_after=3,
    )
    await _sleep(3)
    await ctx.message.delete()


# ? Avatar Command (Owner Only)

@bot.command(hidden=True)
@commands.is_owner()
async def avatar(ctx, avatar_url):
    async with aiohttp.ClientSession() as aioClient:
        async with aioClient.get(avatar_url) as resp:
            new_avatar = await resp.read()
            await bot.user.edit(avatar=new_avatar)
            await ctx.send("Avatar changed!")


# ? Guildlist Command (Owner Only)

@bot.command(hidden=True)
@commands.is_owner()
@commands.bot_has_permissions(attach_files=True)
async def guildlist(ctx):
    with open("guildlist.csv", "w") as guild_list:
        guild_list.write("Server ID,Server Name,# of Users,Features\n")
        for guild in bot.guilds:
            # Write to csv file (guild name, total member count, region and features)
            guild_list.write(
                f'{guild.id},"{guild.name}",{guild.member_count},{guild.features}\n'
            )

    await ctx.send(file=discord.File("guildlist.csv"))


# ? Start Bot

bot.run(os.getenv('TOKEN'))
