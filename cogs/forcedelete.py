import discord
from discord.ext import commands
import json
import os


APPROVED_FILE = "approved.json"
ALLVOUCHES_FILE = "allvouches.json"
ADMIN_ROLE_ID = 1344030025489322066


class ForceDelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_data(self, file_path):
        """Load JSON data from a file."""
        if not os.path.exists(file_path):
            return []
        with open(file_path, "r") as f:
            return json.load(f)

    def save_data(self, file_path, data):
        """Save JSON data to a file."""
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    @commands.command()
    async def forcedelete(self, ctx, vouch_id: int = None):
        """Forcefully deletes a vouch by ID (admin-only)."""
       
        if not any(role.id == ADMIN_ROLE_ID for role in ctx.author.roles):
            return await ctx.reply("You don't have permission to use this command.", delete_after=5)

        if vouch_id is None:
            return await ctx.send("Please provide a valid vouch ID.", delete_after=5)


        approved_vouches = self.load_data(APPROVED_FILE)
        all_vouches = self.load_data(ALLVOUCHES_FILE)


        updated_approved = [v for v in approved_vouches if v["id"] != vouch_id]
        updated_all = [v for v in all_vouches if v["id"] != vouch_id]

        if len(approved_vouches) == len(updated_approved):
            return await ctx.send(f"Vouch ID `{vouch_id}` not found.", delete_after=10)


        self.save_data(APPROVED_FILE, updated_approved)
        self.save_data(ALLVOUCHES_FILE, updated_all)

        await ctx.reply(f"Vouch ID `{vouch_id}` has been successfully deleted.", delete_after=10)


async def setup(bot):
    await bot.add_cog(ForceDelete(bot))