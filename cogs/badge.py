import discord
from discord.ext import commands
import json

PROFILE_FILE = "profile.json"

BADGE_EMOJIS = {
    "Owner": "<:owner:1344041796929454190>",
    "Developer": "<:dev:1344213763317829733>",
    "Admin": "<:Admin:1344042067013144718>",
    "Staff": "<:StaffAll:1344041942735913185>",
    "Trusted": "<:trusted:1344213932759453749>",
    "Donator": "<:emoji_6:1344042502969098311>",
    "User": "<:mmmeb:1344041566800576586>"
}

BADGE_ORDER = ["Owner", "Developer", "Admin", "Staff", "Trusted", "Donator", "User"]

class Badge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_profile(self):
        try:
            with open(PROFILE_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_profile(self, data):
        with open(PROFILE_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def update_badge(self, user_id, badge_name):
        profile_data = self.load_profile()
        user_profile = profile_data.setdefault(str(user_id), {})


        if "badges" not in user_profile:
            user_profile["badges"] = []


        if "User" not in user_profile["badges"]:
            user_profile["badges"].append("User")


        if badge_name in user_profile["badges"]:
            user_profile["badges"].remove(badge_name)
            action = "removed"
        else:
            user_profile["badges"].append(badge_name)
            action = "added"


        user_profile["badges"] = sorted(set(user_profile["badges"]), key=lambda b: BADGE_ORDER.index(b))

        self.save_profile(profile_data)
        return action

    async def badge_command(self, ctx, member: discord.Member, badge_name: str):
        if not ctx.author.get_role(1344030014223548560):
            return await ctx.reply("You don't have permission to manage badges.", delete_after=10)

        if badge_name not in BADGE_EMOJIS:
            return await ctx.reply("Invalid badge name.", delete_after=10)

        action = self.update_badge(member.id, badge_name)
        await ctx.reply(f"{badge_name} badge {action} for {member.mention}.", delete_after=10)

    @commands.command()
    async def addown(self, ctx, member: discord.Member):
        await self.badge_command(ctx, member, "Owner")

    @commands.command()
    async def adddev(self, ctx, member: discord.Member):
        await self.badge_command(ctx, member, "Developer")

    @commands.command()
    async def addadmin(self, ctx, member: discord.Member):
        await self.badge_command(ctx, member, "Admin")

    @commands.command()
    async def addstaff(self, ctx, member: discord.Member):
        await self.badge_command(ctx, member, "Staff")

    @commands.command()
    async def addtrusted(self, ctx, member: discord.Member):
        await self.badge_command(ctx, member, "Trusted")

    @commands.command()
    async def adddonator(self, ctx, member: discord.Member):
        await self.badge_command(ctx, member, "Donator")

async def setup(bot):
    await bot.add_cog(Badge(bot))