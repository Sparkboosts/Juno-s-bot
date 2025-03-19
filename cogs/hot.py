import discord
from discord.ext import commands, tasks
import json
from datetime import datetime, timezone, timedelta

HOT_FILE = "hot.json"
APPROVED_FILE = "approved.json"


def get_hammer_time():
    now = datetime.now(timezone.utc)
    dst_start = datetime(now.year, 3, 31, 2, tzinfo=timezone.utc) - timedelta(days=(datetime(now.year, 3, 31).weekday() + 1) % 7)
    dst_end = datetime(now.year, 10, 31, 2, tzinfo=timezone.utc) - timedelta(days=(datetime(now.year, 10, 31).weekday() + 1) % 7)
    return timezone(timedelta(hours=2)) if dst_start <= now < dst_end else timezone(timedelta(hours=1))

class HotLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_hotboard.start()

    def load_data(self, filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_data(self, filename, data):
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def get_top_users(self):
        approved_vouches = self.load_data(APPROVED_FILE)

        if not isinstance(approved_vouches, list):
            return []

        vouch_counts = {}
        for vouch in approved_vouches:
            if vouch.get("status") == "Approved" and vouch.get("comment") != "Vouch Imported!":
                recipient = vouch.get("recipient", {}).get("id")
                if recipient:
                    vouch_counts[recipient] = vouch_counts.get(recipient, 0) + 1

        return sorted(vouch_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    def update_hot_data(self):
        top_users = self.get_top_users()
        now = datetime.now(get_hammer_time()).timestamp()

        hot_data = {
            "updated_at": now,
            "leaderboard": top_users
        }

        self.save_data(HOT_FILE, hot_data)

    @tasks.loop(minutes=5)
    async def update_hotboard(self):
        self.update_hot_data()

    @commands.command()
    async def hot(self, ctx):
        hot_data = self.load_data(HOT_FILE)

        leaderboard = hot_data.get("leaderboard", [])
        updated_at = hot_data.get("updated_at", datetime.now(get_hammer_time()).timestamp())

        if not leaderboard:
            return await ctx.reply("No approved vouches yet!", delete_after=20)

       
        embed = discord.Embed(
            title="Hot Leaderboard",
            color=discord.Color.dark_blue()
        )

        
        updated_time = f"<t:{int(updated_at)}:R>"
        embed.description = f"**Updated:** {updated_time}\n\n"

        
        for index, (user_id, count) in enumerate(leaderboard, start=1):
            user = await self.bot.fetch_user(user_id)
            embed.description += f"`[{index}]` | {user.name if user else 'Unknown User'} | Count - ``{count}``\n"

        embed.set_footer(text="Created by UnSeen | RepiX | .gg/repix")
        await ctx.reply(embed=embed, delete_after=250)

   
    @commands.command()
    async def resethot(self, ctx):
        if ctx.author.id != 1328264744242643059:
            return await ctx.reply("You don't have permission to reset the leaderboard.", delete_after=10)

        
        self.save_data(HOT_FILE, {"updated_at": datetime.now(get_hammer_time()).timestamp(), "leaderboard": []})
        await ctx.reply("Hot leaderboard has been reset!", delete_after=20)

    
    @commands.command()
    async def refresh(self, ctx):
        self.update_hot_data()
        await ctx.reply("Hot leaderboard has been refreshed!", delete_after=20)

async def setup(bot):
    await bot.add_cog(HotLeaderboard(bot))