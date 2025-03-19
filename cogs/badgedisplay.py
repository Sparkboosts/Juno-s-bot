import discord
from discord.ext import commands

class Badgedisplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.badges = [
            {"name": "Owner", "emoji": "<:owner:1344041796929454190>"},
            {"name": "Developer", "emoji": "<:dev:1344213763317829733>"},
            {"name": "Admin", "emoji": "<:Admin:1344042067013144718>"},
            {"name": "Staff", "emoji": "<:StaffAll:1344041942735913185>"},
            {"name": "Trusted", "emoji": "<:trusted:1344213932759453749>"},
            {"name": "Donator", "emoji": "<:emoji_6:1344042502969098311>"},
            {"name": "User", "emoji": "<:mmmeb:1344041566800576586>"}
        ]

    @commands.command(aliases=["badges", "badgedisplay"])
    async def badge(self, ctx):
        """Displays all available badges in a straight line."""
        badge_display = "\n".join(f"{badge['emoji']} {badge['name']}" for badge in self.badges)

        embed = discord.Embed(
            title="Available Badges",
            description=badge_display,
            color=0xFFD700
        )

        embed.set_footer(text="Made by UnSeen | RepiX | .gg/repix ")
        embed.set_thumbnail(url=ctx.bot.user.display_avatar.url)

        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Badgedisplay(bot))