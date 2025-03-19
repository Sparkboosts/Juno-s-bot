import discord
from discord.ext import commands
import json
import os


PENDING_FILE = "pending.json"
APPROVED_FILE = "approved.json"
DENIED_FILE = "denied.json"
VERIFICATION_FILE = "verification.json"

STATUS_MAP = {
    "Pending": "`Pending`",
    "Manual Verification": "`Manual Verification`",
    "Approved": "`Approved`",
    "Denied": "`Denied`"
}

class VouchGet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_data(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return []

    def find_vouch_by_id(self, vouch_id):
        """Find a vouch by ID in all statuses."""
        for file, status in [
            (PENDING_FILE, "`Pending 📦`"),
            (APPROVED_FILE, "`Approved ✅`"),
            (DENIED_FILE, "`Denied ❌`"),
            (VERIFICATION_FILE, "`Manual Verification ♻️`")
        ]:
            vouches = self.load_data(file)
            for vouch in vouches:
                if vouch["id"] == vouch_id:
                    vouch["status"] = status
                    return vouch
        return None

    @commands.command()
    @commands.has_role(1344028626806378567) 
    async def get(self, ctx, *vouch_ids: int):
        """Get the status of multiple vouches."""
        if not vouch_ids:
            return await ctx.send("Please provide at least one vouch ID.")
        
        embeds = []
        for vouch_id in vouch_ids:
            vouch = self.find_vouch_by_id(vouch_id)

            if not vouch:
                continue

            status = STATUS_MAP.get(vouch["status"], "Unknown")
            embed = discord.Embed(
                title=f"Vouch Status for #{vouch['id']}",
                color=0x33F000
            )
            embed.add_field(name="Recipient Tag:", value=f"{vouch['recipient']['tag']}", inline=False)
            embed.add_field(name="Giver Tag:", value=f"{vouch['giver']['tag']}", inline=False)
            embed.add_field(name="Vouch Comment:", value=vouch["comment"], inline=False)
            embed.add_field(name="When", value=vouch["date"], inline=False)
            embed.add_field(name="Vouch Status", value=vouch["status"], inline=False)

            embed.set_thumbnail(url=ctx.bot.user.display_avatar.url)
            embeds.append(embed)
        
        if embeds:
            await ctx.reply(embeds=embeds)
        else:
            await ctx.send("No vouches found with the provided IDs.")

async def setup(bot):
    await bot.add_cog(VouchGet(bot))