import discord
from discord.ext import commands
import json

PENDING_FILE = "pending.json"

class MyPending(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_pending_vouches(self):
        try:
            with open(PENDING_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @commands.command()
    async def mypending(self, ctx):
        pending_vouches = self.load_pending_vouches()

        
        user_pending = [v for v in pending_vouches if v.get("recipient", {}).get("id") == ctx.author.id]

        if not user_pending:
            return await ctx.author.send("You have no pending vouches!")

        
        embed = discord.Embed(
            title="Your Pending Vouches",
            color=discord.Color.dark_blue()
        )

        for vouch in user_pending:
            giver = vouch.get("giver", {}).get("tag", "Unknown")
            comment = vouch.get("comment", "No comment provided")
            vouch_id = vouch.get("id", "N/A")
            date = vouch.get("date", "Unknown Date")

            embed.add_field(
                name=f"Vouch #{vouch_id}",
                value=f"**From:** {giver}\n"
                      f"**Date:** {date}\n"
                      f"**Comment:** {comment}",
                inline=False
            )

        embed.set_footer(text="Created by UnSeen | RepiX | .gg/repix")

        try:
            await ctx.author.send(embed=embed)
            await ctx.reply("📨 Check your DMs for your pending vouches!", delete_after=10)
        except discord.Forbidden:
            await ctx.reply("I can't DM you. Please enable your DMs and try again.", delete_after=10)

async def setup(bot):
    await bot.add_cog(MyPending(bot))