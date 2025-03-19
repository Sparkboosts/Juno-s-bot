import discord
from discord.ext import commands
import json
import os

NOPREFIX_FILE = "noprefix.json"
PERMISSIONS_FILE = "np_permissions.json"


MAIN_OWNER_ID = 1345006220813271132

def load_noprefix():
    """Loads the no-prefix users from the JSON file."""
    if not os.path.exists(NOPREFIX_FILE):
        return []
    with open(NOPREFIX_FILE, "r") as f:
        return json.load(f)

def save_noprefix(noprefix_users):
    """Saves the no-prefix users to the JSON file."""
    with open(NOPREFIX_FILE, "w") as f:
        json.dump(noprefix_users, f, indent=4)

def load_permissions():
    """Loads users with permission to manage no-prefix."""
    if not os.path.exists(PERMISSIONS_FILE):
        return [MAIN_OWNER_ID]
    with open(PERMISSIONS_FILE, "r") as f:
        return json.load(f)

def save_permissions(permission_users):
    """Saves users with permission to manage no-prefix."""
    with open(PERMISSIONS_FILE, "w") as f:
        json.dump(permission_users, f, indent=4)

class NoPrefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.noprefix_users = load_noprefix()
        self.permission_users = load_permissions()

    async def refresh_noprefix(self):
        """Refreshes the bot's internal no-prefix list without restarting."""
        self.noprefix_users = load_noprefix()

    async def refresh_permissions(self):
        """Refreshes the permission list dynamically."""
        self.permission_users = load_permissions()

    @commands.command(name="addnp")
    async def add_noprefix(self, ctx, user: discord.User):
        """Adds a user to the no-prefix list (Admin only)."""
        if ctx.author.id not in self.permission_users:
            return await ctx.send(embed=discord.Embed(
                description="<:greentick2:1340400484506271817> **You don’t have permission to use this command!**",
                color=0x303136
            ))

        if user.id in self.noprefix_users:
            return await ctx.send(embed=discord.Embed(
                description=f"<:error_white:1338259829906739251> **{user.mention} is already in the no-prefix list!**",
                color=0x303136
            ))

        self.noprefix_users.append(user.id)
        save_noprefix(self.noprefix_users)
        await self.refresh_noprefix()

        embed = discord.Embed(
            description=f"<:greentick2:1340400484506271817> **Added {user.mention} to the no-prefix list!**",
            color=0x303136
        )
        embed.set_footer(text=f"Managed by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="removenp")
    async def remove_noprefix(self, ctx, user: discord.User):
        """Removes a user from the no-prefix list."""
        if ctx.author.id not in self.permission_users:
            return await ctx.send(embed=discord.Embed(
                description="<:crosss:1340612350616539167> **You don’t have permission to use this command!**",
                color=0x303136
            ))

        if user.id not in self.noprefix_users:
            return await ctx.send(embed=discord.Embed(
                description=f"<:crosss:1340612350616539167> **{user.mention} is not in the no-prefix list!**",
                color=0x303136
            ))

        self.noprefix_users.remove(user.id)
        save_noprefix(self.noprefix_users)
        await self.refresh_noprefix()

        embed = discord.Embed(
            description=f"<:crosss:1340612350616539167> **Removed {user.mention} from the no-prefix list!**",
            color=0x303136
        )
        embed.set_footer(text=f"Managed by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="permsnp")
    async def give_permission(self, ctx, user: discord.User):
        """Gives another user permission to manage no-prefix users."""
        if ctx.author.id != MAIN_OWNER_ID:
            return await ctx.send(embed=discord.Embed(
                description="<:greentick2:1340400484506271817> **Only the main owner can give permission!**",
                color=0x303136
            ))

        if user.id in self.permission_users:
            return await ctx.send(embed=discord.Embed(
                description=f"<:crosss:1340612350616539167> **{user.mention} already has permission!**",
                color=0x303136
            ))

        self.permission_users.append(user.id)
        save_permissions(self.permission_users)
        await self.refresh_permissions()

        embed = discord.Embed(
            description=f"<:greentick2:1340400484506271817> **Granted permission to {user.mention} to manage no-prefix users!**",
            color=0x303136
        )
        embed.set_footer(text=f"Authorized by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="refreshnp")
    async def refresh_noprefix_command(self, ctx):
        """Refreshes the no-prefix list without restarting."""
        if ctx.author.id not in self.permission_users:
            return await ctx.send(embed=discord.Embed(
                description="<:crosss:1340612350616539167> **You don’t have permission to use this command!**",
                color=0x303136
            ))

        await self.refresh_noprefix()

        embed = discord.Embed(
            description="<:greentick2:1340400484506271817> **No-prefix list has been refreshed!**",
            color=0x303136
        )
        embed.set_footer(text=f"Refreshed by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(NoPrefix(bot))