import discord
from discord.ext import commands
import json

PENDING_FILE = "pending.json"

class PendingVouches(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_data(self, filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_data(self, filename, data):
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    @commands.command()
    @commands.has_role(1344028626806378567)
    async def pending(self, ctx, page: int = 1):
        pending_vouches = self.load_data(PENDING_FILE)
        total_vouches = len(pending_vouches)
        max_vouches_per_page = 50

        if total_vouches == 0:
            await ctx.reply("There are no pending vouches.", delete_after=10)
            return

       
        start = (page - 1) * max_vouches_per_page
        end = page * max_vouches_per_page

        if start >= total_vouches:
            await ctx.reply("This page doesn't exist. Please use a valid page number.", delete_after=10)
            return

        vouches_to_display = pending_vouches[start:end]
        embed = discord.Embed(
            title=f"Pending Vouches - Page {page}",
            description=f"Showing {start + 1}-{min(end, total_vouches)} of {total_vouches} pending vouches.",
            color=discord.Color.blue()
        )

        
        vouch_ids = "\n".join([str(vouch.get("id")) for vouch in vouches_to_display])
        embed.add_field(name="Vouch IDs", value=vouch_ids, inline=False)

        
        next_page = page + 1 if end < total_vouches else None
        prev_page = page - 1 if page > 1 else None

        footer_text = "Page {}/{}".format(page, (total_vouches // max_vouches_per_page) + 1)
        if next_page:
            footer_text += f" | Next page: +pending {next_page}"
        if prev_page:
            footer_text += f" | Previous page: +pending {prev_page}"

        embed.set_footer(text=footer_text)

        await ctx.reply(embed=embed, delete_after=500)

async def setup(bot):
    await bot.add_cog(PendingVouches(bot))