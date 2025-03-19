import discord
from discord.ext import commands
import json

PENDING_FILE = "pending.json"

VERIFIER_ROLE_ID = 1344028626806378567

class ViewPending(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_data(self):
        try:
            with open(PENDING_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def has_permission(self, ctx, role_id):
        return any(role.id == role_id for role in ctx.author.roles)

    @commands.command()
    async def viewpending(self, ctx, member: discord.Member):
        if not self.has_permission(ctx, VERIFIER_ROLE_ID):
            return await ctx.reply("You don't have permission to use this command.", delete_after=5)

        pending_vouches = self.load_data()

        user_pending = [v for v in pending_vouches if v.get("recipient", {}).get("id") == member.id]

        if not user_pending:
            return await ctx.reply(f"No pending vouches found for {member.display_name}.", delete_after=10)

        vouch_ids = [v["id"] for v in user_pending]

        embed = discord.Embed(
            title=f"Pending Vouches for {member.display_name}",
            description="\n".join(map(str, vouch_ids)),
            color=0x2CCF00
        )


        embed.set_footer(text="Created by UnSeen | discord.gg/repix")

        await ctx.reply(embed=embed, delete_after=20)

async def setup(bot):
    await bot.add_cog(ViewPending(bot))