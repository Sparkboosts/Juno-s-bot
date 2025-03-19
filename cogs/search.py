import discord
from discord.ext import commands
import json

PROFILE_FILE = "profile.json"

class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_data(self, filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def load_profiles(self):
        return self.load_data(PROFILE_FILE)

    @commands.command(aliases=["find"])
    async def search(self, ctx, *, query: str):
        profiles = self.load_profiles()
        query = query.lower().strip()

        matching_users = []

        for user_id, profile in profiles.items():
            product_field = profile.get("product", [])

            
            if isinstance(product_field, str):
                product_field = [p.strip() for p in product_field.split(",") if p.strip()]

            
            products = [p.lower() for p in product_field]
            if any(query in product for product in products):
                user = await self.bot.fetch_user(int(user_id))
                matching_users.append(f"**{user.display_name}** ({user.mention})")

        if not matching_users:
            return await ctx.reply(f"No users found with the product: `{query}`", delete_after=20)

        embed = discord.Embed(
            title=f"Search Results for: `{query}`",
            description="\n".join(matching_users),
            color=0x00008B
        )

        await ctx.reply(embed=embed, delete_after=100)

async def setup(bot):
    await bot.add_cog(Search(bot))