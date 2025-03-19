import discord
from discord.ext import commands
import json
import os


APPROVED_FILE = "approved.json"
PENDING_FILE = "pending.json"
PROFILE_FILE = "profile.json"
USED_IDS_FILE = "used_ids.json"

VOUCH_MANAGER_ROLE_ID = 1344030025489322066

LOG_CHANNEL_ID = 1345008546647117834


class VouchManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        for file in [APPROVED_FILE, PENDING_FILE, PROFILE_FILE, USED_IDS_FILE]:
            if not os.path.exists(file):
                with open(file, "w") as f:
                    json.dump([] if file != PROFILE_FILE else {}, f)

    def load_data(self, filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return [] if filename != PROFILE_FILE else {}

    def save_data(self, filename, data):
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    async def log_action(self, action, member, amount=None, target=None):
        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            if action == "Transfer":
                await log_channel.send(f"**Transfer:** All vouches and profile of `{member}` → `{target}`")
            else:
                await log_channel.send(f"**{action} Vouch:** `{amount}` vouch(es) for `{member}`")

    def has_permission(self, ctx):
        return any(role.id == VOUCH_MANAGER_ROLE_ID for role in ctx.author.roles)

    def get_next_vouch_id(self):
        """Fetch the next available vouch ID."""
        used_ids = self.load_data(USED_IDS_FILE)
        return max(used_ids, default=0) + 1

    def update_used_ids(self, new_ids):
        """Update the used_ids.json with new vouch IDs."""
        used_ids = self.load_data(USED_IDS_FILE)
        used_ids.extend(new_ids)
        self.save_data(USED_IDS_FILE, used_ids)

    async def get_user(self, user_input):
        """Fetch a user by ID, mention, or username (works for users outside the server)."""
        try:
            # Try fetching by ID
            user = await self.bot.fetch_user(int(user_input))
            return user
        except (ValueError, discord.NotFound):
            # Try fetching by mention or username
            if user_input.startswith("<@") and user_input.endswith(">"):
                user_id = int(user_input.strip("<@!>"))
                return await self.bot.fetch_user(user_id)
            else:
                # Search by username
                for member in self.bot.get_all_members():
                    if member.name == user_input or member.display_name == user_input:
                        return member
        return None

    @commands.command()
    async def addvouch(self, ctx, member: str, amount: int):
        if not self.has_permission(ctx):
            return await ctx.send("You do not have permission to use this command.", delete_after=5)

        member = await self.get_user(member)
        if not member:
            return await ctx.send("User not found. Ensure you provide a valid ID, mention, or username.", delete_after=5)

        approved_data = self.load_data(APPROVED_FILE)

        start_id = self.get_next_vouch_id()
        new_ids = list(range(start_id, start_id + amount))

        for vouch_id in new_ids:
            new_vouch = {
                "id": vouch_id,
                "recipient": {"id": member.id, "tag": str(member)},
                "giver": {"id": ctx.author.id, "tag": str(ctx.author)},
                "comment": "Vouch Imported!",
                "date": str(ctx.message.created_at),
                "status": "Approved"
            }
            approved_data.append(new_vouch)

        self.save_data(APPROVED_FILE, approved_data)
        self.update_used_ids(new_ids)

        await ctx.send(f"Added {amount} vouch(es) to {member}.", delete_after=5)
        await self.log_action("Add", member, amount)

    @commands.command()
    async def removevouch(self, ctx, member: str, amount: int):
        if not self.has_permission(ctx):
            return await ctx.send("You do not have permission to use this command.", delete_after=5)

        member = await self.get_user(member)
        if not member:
            return await ctx.send("User not found. Ensure you provide a valid ID, mention, or username.", delete_after=5)

        approved_data = self.load_data(APPROVED_FILE)

        updated_data = []
        removed = 0
        for v in approved_data:
            if v["recipient"]["id"] == member.id and removed < amount:
                removed += 1
            else:
                updated_data.append(v)

        self.save_data(APPROVED_FILE, updated_data)

        await ctx.send(f"Removed {removed} vouch(es) from {member}.", delete_after=5)
        await self.log_action("Remove", member, removed)

    @commands.command()
    async def resetvouch(self, ctx, member: str):
        if not self.has_permission(ctx):
            return await ctx.send("You do not have permission to use this command.", delete_after=5)

        member = await self.get_user(member)
        if not member:
            return await ctx.send("User not found. Ensure you provide a valid ID, mention, or username.", delete_after=5)

        approved_data = self.load_data(APPROVED_FILE)
        pending_data = self.load_data(PENDING_FILE)
        profile_data = self.load_data(PROFILE_FILE)

        approved_data = [v for v in approved_data if v["recipient"]["id"] != member.id]
        pending_data = [v for v in pending_data if v["recipient"]["id"] != member.id]

        profile_data.pop(str(member.id), None)

        self.save_data(APPROVED_FILE, approved_data)
        self.save_data(PENDING_FILE, pending_data)
        self.save_data(PROFILE_FILE, profile_data)

        await ctx.send(f"Reset all vouches and profile for {member}.", delete_after=5)
        await self.log_action("Reset", member)

    @commands.command()
    async def transferprofile(self, ctx, member1: str, member2: str):
        if not self.has_permission(ctx):
            return await ctx.send("You do not have permission to use this command.", delete_after=5)

        member1 = await self.get_user(member1)
        member2 = await self.get_user(member2)

        if not member1 or not member2:
            return await ctx.send("One or both users not found. Ensure you provide valid IDs, mentions, or usernames.", delete_after=5)

        approved_data = self.load_data(APPROVED_FILE)
        pending_data = self.load_data(PENDING_FILE)
        profile_data = self.load_data(PROFILE_FILE)

        for vouch in approved_data + pending_data:
            if vouch["recipient"]["id"] == member1.id:
                vouch["recipient"]["id"] = member2.id
                vouch["recipient"]["tag"] = str(member2)

        if str(member1.id) in profile_data:
            profile_data[str(member2.id)] = profile_data.pop(str(member1.id))

        self.save_data(APPROVED_FILE, approved_data)
        self.save_data(PENDING_FILE, pending_data)
        self.save_data(PROFILE_FILE, profile_data)

        await ctx.send(f"Transferred profile and vouches from {member1} to {member2}.", delete_after=5)
        await self.log_action("Transfer", member1, target=member2)


async def setup(bot):
    await bot.add_cog(VouchManagement(bot))