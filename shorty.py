import aiohttp
import discord
from discord.ext import commands
import pyshorteners
import statcord
import sentry_sdk
import psutil
import platform
from datetime import datetime
import logging
from traceback import format_exc
from discord import Embed
from asyncio import sleep as _sleep
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


sentry_sdk.init(
    "YOUR_SENTRY_URL",
    traces_sample_rate=1.0, release="shorty@1.0.0", sample_rate=0.25)


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


class shortners():
    def __init__(self):
        self.bitly = pyshorteners.Shortener(
            api_key="YOUR_API_KEY").bitly
        self.chilpit = pyshorteners.Shortener().chilpit
        self.clckru = pyshorteners.Shortener().clckru
        self.cuttly = pyshorteners.Shortener(
            api_key="YOUR_API_KEY").cuttly
        self.dagd = pyshorteners.Shortener().dagd
        self.osdb = pyshorteners.Shortener().osdb
        self.shortcm = pyshorteners.Shortener(
            api_key="YOUR_API_KEY", domain="3adu.short.gy").shortcm
        self.tinyurl = pyshorteners.Shortener().tinyurl


# Initiate Bot
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("?"), help_command=None)

# Initiate Jishaku
bot.load_extension('jishaku')

# Initate URLValidator
urlvalidator = URLValidator()

# Initiate Shorteners
shortner = shortners()

# Initiate Statcord
statcord_key = "YOUR_API_KEY"
api = statcord.Client(bot, statcord_key)
api.start_loop()

# Initiate Logger
logger = logging.getLogger(__name__)

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('bot.log')
c_handler.setLevel(logging.WARNING)
f_handler.setLevel(logging.ERROR)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)


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


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"?help in {len(bot.guilds)} servers!"))
    print("""
                        _______           _______  _______ _________         
                        (  ____ \|\     /|(  ___  )(  ____ )\__   __/|\     /|
                        | (    \/| )   ( || (   ) || (    )|   ) (   ( \   / )
                        | (_____ | (___) || |   | || (____)|   | |    \ (_) / 
                        (_____  )|  ___  || |   | ||     __)   | |     \   /  
                              ) || (   ) || |   | || (\ (      | |      ) (   
                        /\____) || )   ( || (___) || ) \ \__   | |      | |   
                        \_______)|/     \|(_______)|/   \__/   )_(      \_/  """)
    print("="*40, "System Information", "="*40)
    uname = platform.uname()
    print(f"System: {uname.system}")
    print(f"Node Name: {uname.node}")
    print(f"Release: {uname.release}")
    print(f"Version: {uname.version}")
    print(f"Machine: {uname.machine}")
    print(f"Processor: {uname.processor}")
# 52
    # Boot Time
    print("="*40, "Boot Time", "="*40)
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    print(
        f"Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}")

    # let's print CPU information
    print("="*40, "CPU Info", "="*40)
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
    print("="*40, "Memory Information", "="*40)
    # get the memory details
    svmem = psutil.virtual_memory()
    print(f"Total: {get_size(svmem.total)}")
    print(f"Available: {get_size(svmem.available)}")
    print(f"Used: {get_size(svmem.used)}")
    print(f"Percentage: {svmem.percent}%")
    print("="*40, "Logs", "="*40)
    logger.warning('We have logged in as {0.user}'.format(bot))


@bot.event
async def on_guild_join(guild):
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"?help in {len(bot.guilds)} servers!"))


@bot.event
async def on_guild_remove(guild):
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"?help in {len(bot.guilds)} servers!"))


@bot.event
async def on_command(ctx):
    api.command_run(ctx)


@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def bitly(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(title=shortner.bitly.short(
            link), color=0x0055ff).set_footer(text="Requested By " + ctx.author.name)
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def chilpit(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(title=shortner.chilpit.short(link), color=0x0055ff).set_footer(
            text="Requested By " + ctx.author.name)
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def clckru(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(title=shortner.clckru.short(
            link), color=0x0055ff).set_footer(text="Requested By " + ctx.author.name)
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def cuttly(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(title=shortner.cuttly.short(
            link), color=0x0055ff).set_footer(text="Requested By " + ctx.author.name)
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def dagd(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(title=shortner.dagd.short(
            link), color=0x0055ff).set_footer(text="Requested By " + ctx.author.name)
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def osdb(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(title=shortner.osdb.short(
            link), color=0x0055ff).set_footer(text="Requested By " + ctx.author.name)
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def shortcm(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(title=shortner.shortcm.short(
            link), color=0x0055ff).set_footer(text="Requested By " + ctx.author.name)
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


@commands.cooldown(2, 30, commands.BucketType.user)
@bot.command()
async def tinyurl(ctx, link):
    try:
        urlvalidator(link)
        embed = Embed(title=shortner.tinyurl.short(
            link), color=0x0055ff).set_footer(text="Requested By " + ctx.author.name)
        await ctx.send(embed=embed)
    except ValidationError:
        await ctx.send("Please Input A Valid Link!")


@bot.command()
async def donate(ctx):
    embed = Embed(title="Donation Options",
                  description="You can donate us from the following options:", color=0x0055ff)
    embed.set_thumbnail(
        url="https://www.goodwillaz.org/wordpress/wp-content/uploads/2018/04/5-15-1.jpg")
    embed.add_field(
        name="Bitcoin", value="bc1q0zrhcrk70jtccyaphxx79p92pkdpwa5jagylk6", inline=False)
    embed.add_field(
        name="Paypal", value="https://paypal.me/rjdj0261", inline=False)
    embed.add_field(
        name="UPI", value="unknowncoder0261@okhdfcbank", inline=False)
    embed.set_footer(text="Requested by " + ctx.author.name)
    await ctx.send(embed=embed)


@bot.command()
async def invite(ctx):
    embed = Embed(title="Invite The Bot", description="[https://dsc.gg/shorty](https://dsc.gg/shorty)",
                  color=0x0055ff).set_footer(text="Requested By " + ctx.author.name)
    await ctx.send(embed=embed)


@bot.command()
async def support(ctx):
    embed = Embed(title="Join The Support Server", description="[https://dsc.gg/shorty-support](https://dsc.gg/shorty-support)",
                  color=0x0055ff).set_footer(text="Requested By " + ctx.author.name)
    await ctx.send(embed=embed)


@bot.command()
async def ping(ctx):
    embed = Embed(color=0x0055ff).add_field(
        name="Ping", value=bot.latency, inline=False).set_footer(text="Requested By " + ctx.author.name)
    await ctx.send(embed=embed)


@bot.command()
async def help(ctx):
    embed = Embed(title="List Of Commands",
                  description="Every Command Has A Cooldown of 30 seconds!", color=0x0055ff)
    embed.add_field(
        name="bitly", value="Shorten Your Link Using Bitly.", inline=False)
    embed.add_field(
        name="chilpit", value="Shorten Your Link Using Chilpit.", inline=False)
    embed.add_field(
        name="clckru", value="Shorten Your Link Using Clckru.", inline=False)
    embed.add_field(
        name="cuttly", value="Shorten Your Link Using Cuttly.", inline=False)
    embed.add_field(
        name="dagd", value="Shorten Your Link Using Dagd.", inline=False)
    embed.add_field(
        name="osdb", value="Shorten Your Link Using Osdb.", inline=False)
    embed.add_field(
        name="shortcm", value="Shorten Your Link Using Shortcm.", inline=False)
    embed.add_field(
        name="tinyurl", value="Shorten Your Link Using Tinyurl.", inline=False)
    embed.add_field(
        name="donate", value="Donate The Developer Of The Bot", inline=False)
    embed.add_field(
        name="invite", value="Invite The Bot To Your Server", inline=False)
    embed.add_field(
        name="support", value="Join The Support Server Of The Bot", inline=False)
    embed.add_field(
        name="ping", value="Ping Of The Bot", inline=False)
    embed.set_footer(text="Requested By " + ctx.author.name)
    await ctx.send(embed=embed)


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
            locals()
        )

        await locals()["__function"]()
    except:
        await ctx.send(
            embed=Embed(title="Error!", description=f"```{format_exc()}```", color=discord.Color.red()).set_footer(
                text=f"Invoker: {ctx.author}", icon_url=ctx.author.avatar_url_as(format="png")))


@eval_.error
async def eval__error(ctx, error):
    await ctx.send(embed=Embed(title="Error!", description=f"```{error}```", color=discord.Color.red()).set_footer(
        text=f"Invoker: {ctx.author}", icon_url=ctx.author.avatar_url_as(format="png")))


@bot.command(hidden=True)
@commands.is_owner()
async def selfpurge(ctx, amount=2):
    amount = int(amount)

    def fusion(m):
        return bot.user.id == m.author.id

    await ctx.message.channel.purge(limit=amount, check=fusion, bulk=False)
    await ctx.send(embed=Embed(title="Purged",
                               description=f"{ctx.author.mention} i have successfully purged `{amount}` of messages in <#{ctx.message.channel.id}>",
                               color=ctx.author.color), delete_after=3)
    await _sleep(3)
    await ctx.message.delete()


@bot.command(hidden=True)
@commands.is_owner()
async def avatar(ctx, avatar_url):
    async with aiohttp.ClientSession() as aioClient:
        async with aioClient.get(avatar_url) as resp:
            new_avatar = await resp.read()
            await bot.user.edit(avatar=new_avatar)
            await ctx.send('Avatar changed!')


@bot.command(hidden=True)
@commands.is_owner()
@commands.bot_has_permissions(attach_files=True)
async def guildlist(ctx):
    with open('guildlist.csv', 'w') as guild_list:
        guild_list.write('Server ID,Server Name,# of Users,Features\n')
        for guild in bot.guilds:
            # Write to csv file (guild name, total member count, region and features)
            guild_list.write(
                f'{guild.id},"{guild.name}",{guild.member_count},{guild.features}\n')

    await ctx.send(file=discord.File('guildlist.csv'))


bot.run('YOUR_BOT_TOKEN')
