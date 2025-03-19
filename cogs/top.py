import discord
from discord.ext import commands
import json
from collections import Counter

APPROVED_FILE = "approved.json"

class TopVouch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    def load_data(self, filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    
    def get_top_users(self):
        approved_vouches = self.load_data(APPROVED_FILE)

        if not isinstance(approved_vouches, list):
            return []

        
        vouch_counts = Counter(vouch["recipient"]["id"] for vouch in approved_vouches if vouch.get("status") == "Approved")

        
        return vouch_counts.most_common(10)

    
    @commands.command()
    async def top(self, ctx):
        top_users = self.get_top_users()

        if not top_users:
            return await ctx.reply("No approved vouches available yet!", delete_after=20)

        
        embed = discord.Embed(
            title="**Vouch Leaderboard**",
            description="These users have the most approved vouches!",
            color=discord.Color.dark_blue()
        )

        
        leaderboard = ""
        for index, (user_id, count) in enumerate(top_users, start=1):
            user = await self.bot.fetch_user(user_id)
            username = user.name if user else "Unknown User"
            leaderboard += f"`[{index}]` | **{username}** | Count - `{count}`\n"

        embed.add_field(name="**Leaderboard**", value=leaderboard, inline=False)

        
        embed.set_footer(text="Updated in real-time | RepiX | .gg/repix"
        await ctx.reply(embed=embed, delete_after=150)

async def setup(bot):
    await bot.add_cog(TopVouch(bot))