import discord
from discord.ext import commands
import json
import os

with open("config.json", "r") as f:
    config = json.load(f)

NOPREFIX_FILE = "noprefix.json"

def load_noprefix_users():
    """Loads the latest no-prefix users from the JSON file."""
    try:
        with open(NOPREFIX_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

noprefix_users = load_noprefix_users()

async def get_prefix(bot, message):
    """Np"""
    base_prefixes = [config["prefix"], f"<@{bot.user.id}> ", f"<@!{bot.user.id}> "]  

    if message.author.id in noprefix_users:
        return base_prefixes + [""]  

    return base_prefixes  


owner_ids = [1328264744242643059]
intents = discord.Intents.all()

os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"


bot = commands.Bot(command_prefix=get_prefix, intents=intents, case_insensitive=True)

bot.owner_ids = set(owner_ids)  
bot.remove_command("help")

def is_owner():
    async def predicate(ctx):
        return ctx.author.id in bot.owner_ids
    return commands.check(predicate)


@bot.command()
@is_owner()
async def shutdown(ctx):
    """Shutdown bot (own)."""
    await ctx.send("Shutting down...")
    await bot.close()

@bot.command()
@is_owner()
async def leave(ctx, guild_id: int):
    """Leaves a sv (own)."""
    guild = bot.get_guild(guild_id)
    if guild:
        await guild.leave()
        await ctx.send(f"Left `{guild.name}` (`{guild.id}`)")
    else:
        await ctx.send("Invalid Guild ID.")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    
    global noprefix_users
    noprefix_users = load_noprefix_users()

    if message.author.id in noprefix_users:  
        ctx = await bot.get_context(message)
        if ctx.valid:
            await bot.invoke(ctx)  
            return  

    await bot.process_commands(message)  


async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} |Made by Flaah")
    await load_cogs()
    await bot.load_extension("jishaku")


bot.run(config["token"])