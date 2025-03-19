import discord
from discord.ext import commands
import json
import os

SCAMMER_FILE = "scammer.json"
BLACKLIST_FILE = "blacklist.json"
MARK_ROLE_ID = 1345005106432577627

class Mark(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_data(self, filename):
        if not os.path.exists(filename):
            return {}  
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    
                    return {str(user_id): True for user_id in data}
                return data
        except (json.JSONDecodeError, ValueError):
            return {}  

    def save_data(self, filename, data):
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    @commands.command()
    @commands.has_role(MARK_ROLE_ID)
    async def mark(self, ctx, member: discord.Member, *, reason: str):
        scammer_data = self.load_data(SCAMMER_FILE)
        blacklist_data = self.load_data(BLACKLIST_FILE)

        user_id = str(member.id)

       
        if user_id in scammer_data:
            return await ctx.reply(f"{member.display_name} is already marked as a scammer.", delete_after=10)

       
        scammer_data[user_id] = reason
        blacklist_data[user_id] = True

        self.save_data(SCAMMER_FILE, scammer_data)
        self.save_data(BLACKLIST_FILE, blacklist_data)

        await ctx.reply(f"{member.display_name} has been marked as a scammer.", delete_after=10)

    @commands.command()
    @commands.has_role(MARK_ROLE_ID)
    async def unmark(self, ctx, member: discord.Member):
        scammer_data = self.load_data(SCAMMER_FILE)
        blacklist_data = self.load_data(BLACKLIST_FILE)

        user_id = str(member.id)

        
        if user_id not in scammer_data:
            return await ctx.reply(f"{member.display_name} is not marked as a scammer.", delete_after=10)

       
        del scammer_data[user_id]
        blacklist_data.pop(user_id, None)

        self.save_data(SCAMMER_FILE, scammer_data)
        self.save_data(BLACKLIST_FILE, blacklist_data)

        await ctx.reply(f"{member.display_name} has been unmarked as a scammer.", delete_after=10)

async def setup(bot):
    await bot.add_cog(Mark(bot))