import discord
from discord.ext import commands
import json

PROFILE_FILE = "profile.json"
BLACKLIST_ROLE = 1345004589589598210

class Blacklist(commands.Cog):
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

    def update_blacklist_status(self, user_id, status):
        profile_data = self.load_profile()
        user_profile = profile_data.setdefault(str(user_id), {})
        user_profile["blacklisted"] = status
        self.save_profile(profile_data)

    @commands.command()
    @commands.has_role(BLACKLIST_ROLE)
    async def blacklist(self, ctx, member: discord.Member):
        """Blacklist a user from vouching."""
        self.update_blacklist_status(member.id, True)
        await ctx.reply(f"{member.display_name} has been blacklisted from vouching.", delete_after=10)

    @commands.command()
    @commands.has_role(BLACKLIST_ROLE)
    async def unblacklist(self, ctx, member: discord.Member):
        """Remove a user from the blacklist."""
        self.update_blacklist_status(member.id, False)
        await ctx.reply(f"{member.display_name} has been removed from the blacklist.", delete_after=10)

async def setup(bot):
    await bot.add_cog(Blacklist(bot))