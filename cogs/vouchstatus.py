import discord
from discord.ext import commands
import json
import os


PENDING_FILE = "pending.json"
APPROVED_FILE = "approved.json"
DENIED_FILE = "denied.json"
VERIFICATION_FILE = "verification.json"


STATUS_MAP = {
    "Pending": "`Pending 📥`",
    "Manual Verification": "`Manual Verification ⚡`",
    "Approved": "`Approved ✅`",
    "Denied": "`Denied ❌`"
}

class VouchStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_data(self, file_path):
        """Load data from a JSON file."""
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return []

    def find_user_vouch(self, user_id, vouch_id):
        """Find a vouch by ID for a specific recipient."""
        for file, status in [
            (PENDING_FILE, "Pending"),
            (APPROVED_FILE, "Approved"),
            (DENIED_FILE, "Denied"),
            (VERIFICATION_FILE, "Manual Verification")
        ]:
            vouches = self.load_data(file)
            for vouch in vouches:
                if vouch["id"] == vouch_id and str(vouch["recipient"]["id"]) == str(user_id):
                    vouch["status"] = STATUS_MAP[status]
                    return vouch
        return None

    @commands.command(name="status")
    async def status(self, ctx, *vouch_ids: int):
        """Check the status of your own vouches."""
        if not vouch_ids:
            return await ctx.reply("**Please provide at least one vouch ID**")

        embeds = []
        for vouch_id in vouch_ids:
            vouch = self.find_user_vouch(ctx.author.id, vouch_id)

            if not vouch:
                embed = discord.Embed(
                    title="Vouch ID not found.",
                    description=f"Vouch with ID `{vouch_id}` not found or doesn't belong to you.",
                    color=discord.Color.red()
                )
                embeds.append(embed)
                continue

            embed = discord.Embed(
                title=f"Vouch Status for #{vouch['id']}",
                color=0x1D3557  
            )
            embed.add_field(name="Recipient Tag", value=vouch["recipient"]["tag"], inline=False)
            embed.add_field(name="Giver Tag", value=vouch["giver"]["tag"], inline=False)
            embed.add_field(name="Vouch Comment", value=vouch["comment"], inline=False)
            embed.add_field(name="When", value=vouch["date"], inline=False)
            embed.add_field(name="Vouch Status", value=vouch["status"], inline=False)

            embed.set_thumbnail(url=self.bot.user.display_avatar.url)

            embeds.append(embed)

        
        try:
            for embed in embeds:
                await ctx.author.send(embed=embed)
            await ctx.reply(" **Check your DMs for vouch status.**", delete_after=10)
        except discord.Forbidden:
            await ctx.reply("**I couldn't DM you. Please enable DMs and try again.**", delete_after=10)

async def setup(bot):
    await bot.add_cog(VouchStatus(bot))