import discord
from discord.ext import commands
import time
import datetime

BOT_INVITE_URL = "https://discord.com/oauth2/authorize?client_id=1345347442484445245&permissions=265280&scope=bot"

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    @commands.command()
    async def invite(self, ctx):
        embed = discord.Embed(
            title="Invite Me!",
            description="Click the button below to invite me to your server.",
            color=discord.Color.dark_blue()
        )
        embed.set_footer(text="Created by UnSeen | RepiX | .gg/repix")

        view = discord.ui.View()
        button = discord.ui.Button(label="Invite Me", url=BOT_INVITE_URL, style=discord.ButtonStyle.link)
        view.add_item(button)

        await ctx.reply(embed=embed, view=view, delete_after=60)

    @commands.command()
    async def uptime(self, ctx):
        current_time = time.time()
        uptime_seconds = int(current_time - self.start_time)

        uptime_str = str(datetime.timedelta(seconds=uptime_seconds))

        embed = discord.Embed(
            title="Bot Uptime",
            description=f"**I've been running for:** `{uptime_str}`",
            color=discord.Color.dark_blue()
        )
        embed.set_footer(text="Created by UnSeen | RepiX | .gg/repix")

        await ctx.reply(embed=embed, delete_after=60)

    @commands.command()
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)  # Latency in ms
        await ctx.reply(f"🏓 **Pong!** Latency: `{latency}ms`", delete_after=200)

async def setup(bot):
    await bot.add_cog(General(bot))