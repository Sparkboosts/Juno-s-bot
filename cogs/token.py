import discord
from discord.ext import commands
import json
import os
import random
import string
from datetime import datetime


TOKEN_FILE = "tokens.json"
ADMIN_ROLE_ID = 1344030025489322066


class TokenSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


        if not os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "w") as f:
                json.dump({}, f)

    def load_tokens(self):
        """Load token data from the JSON file."""
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)

    def save_tokens(self, data):
        """Save token data to the JSON file."""
        with open(TOKEN_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def generate_token(self):
        """Generate a unique 30-character token."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=30))

    @commands.command()
    async def token(self, ctx):
        """Generate a unique token for the user and DM it."""
        user = ctx.author


        tokens = self.load_tokens()


        new_token = self.generate_token()

        
        tokens[str(user.id)] = {
            "token": new_token,
            "user_id": user.id,
            "user_name": str(user),
            "generated_at": str(datetime.utcnow())
        }


        self.save_tokens(tokens)


        try:
            await user.send(f" **Your New Unique Token:**\n```{new_token}```\n(Note: This token is now active, and any previous token is invalid, please do not share this with anyone.")
            await ctx.reply("Your unique token has been sent to your DMs.", delete_after=10)
        except discord.Forbidden:
            await ctx.reply("I couldn't DM you. Please check your privacy settings.", delete_after=10)

    @commands.command()
    async def tokenview(self, ctx, token: str = None):
        """View token information (admin-only)."""

        if not any(role.id == ADMIN_ROLE_ID for role in ctx.author.roles):
            return await ctx.reply("You don't have permission to use this command.", delete_after=5)


        if not token:
            return await ctx.reply("Please provide a token.", delete_after=10)


        tokens = self.load_tokens()


        matching_user = next((user for user in tokens.values() if user["token"] == token), None)

        if not matching_user:
            return await ctx.send("Invalid or expired token.", delete_after=10)

        
        embed = discord.Embed(
            title="Token Information",
            color=0x33F000
        )
        embed.add_field(name=" User Tag:", value=f"`{matching_user['user_name']}`", inline=False)
        embed.add_field(name="User ID", value=f"`{matching_user['user_id']}`", inline=False)
        embed.add_field(name="Generated At", value=f"`{matching_user['generated_at']}`", inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(TokenSystem(bot))