import discord
from discord.ext import commands
import json
import os


APPROVED_FILE = "approved.json"
MOD_ROLE_ID = 1344028626806378567


class Vouches(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_data(self, file_path):
        """Load JSON data from a file."""
        if not os.path.exists(file_path):
            return []
        with open(file_path, "r") as f:
            return json.load(f)

    @commands.command()
    async def vouches(self, ctx, member: discord.Member = None):
        """Sends a user's total approved vouch IDs in a text file (mod-only)."""
        
        if not any(role.id == MOD_ROLE_ID for role in ctx.author.roles):
            return await ctx.send("You don't have permission to use this command.", delete_after=5)


        if not member:
            return await ctx.send("Please specify a user.", delete_after=5)


        approved_vouches = self.load_data(APPROVED_FILE)


        user_vouches = [vouch["id"] for vouch in approved_vouches if vouch["recipient"]["id"] == member.id]


        if not user_vouches:
            return await ctx.send(f"**{member}** has no approved vouches.", delete_after=5)


        file_path = f"/tmp/{member.id}_vouches.txt"
        with open(file_path, "w") as f:
            f.write("\n".join(map(str, user_vouches)))


        await ctx.reply(f"Vouches for **{member}**:", file=discord.File(file_path))


        os.remove(file_path)


async def setup(bot):
    await bot.add_cog(Vouches(bot))