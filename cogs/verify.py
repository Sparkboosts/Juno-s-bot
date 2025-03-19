import discord
from discord.ext import commands
import json
import os

PENDING_FILE = "pending.json"
APPROVED_FILE = "approved.json"
DENIED_FILE = "denied.json"
VERIFICATION_FILE = "verification.json"
ALLVOUCHES_FILE = "allvouches.json"


VERIFIER_ROLE = 1344028626806378567
ADMIN_OVERRIDE_ROLE = 1344030025489322066

class VouchVerify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 1345008490569273435

    def load_data(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return []

    def save_data(self, file_path, data):
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    def find_vouch_by_id(self, vouch_id, file_path):
        """Find and remove a vouch by ID from a specific file."""
        vouches = self.load_data(file_path)
        for vouch in vouches:
            if vouch["id"] == vouch_id:
                vouches.remove(vouch)
                self.save_data(file_path, vouches)
                return vouch
        return None

    def move_vouch(self, vouch, to_file, status):
        """Move a vouch to a new status and file."""
        vouch["status"] = status
        vouches = self.load_data(to_file)
        vouches.append(vouch)
        self.save_data(to_file, vouches)

    async def log_action(self, ctx, vouch, status):
        """Send a log message when a vouch is processed."""
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            embed = discord.Embed(
                title=f"Vouch {status}",
                color=0x33F000
            )
            embed.add_field(name="Vouch ID", value=f"`{vouch['id']}`", inline=False)
            embed.add_field(name="Recipient Tag:", value=f"{vouch['recipient']['tag']} (ID: {vouch['recipient']['id']})", inline=False)
            embed.add_field(name="Giver Tag:", value=f"{vouch['giver']['tag']} (ID: {vouch['giver']['id']})", inline=False)
            embed.add_field(name="Vouch Comment:", value=vouch["comment"], inline=False)
            embed.add_field(name="Verified by:", value=f"{ctx.author} (ID: {ctx.author.id})", inline=False)
            embed.add_field(name="Vouch Status:", value=status, inline=False)
            embed.set_footer(text="Created by UnSeen | RepiX| .gg/repix")
            await log_channel.send(embed=embed)

    async def notify_user(self, user_id, title, description):
        """Send a DM notification to the user."""
        user = self.bot.get_user(user_id)
        if user:
            try:
                embed = discord.Embed(title=title, description=description, color=0x00008B)
                await user.send(embed=embed)
            except discord.Forbidden:
                pass

    @commands.command()
    @commands.has_role(VERIFIER_ROLE)
    async def approve(self, ctx, *vouch_ids: int):
        """Approve multiple pending or manual verification vouches."""
        if not vouch_ids:
            return await ctx.send("You need to specify vouch IDs.")

        approved_vouches = []
        for vouch_id in vouch_ids:
            vouch = self.find_vouch_by_id(vouch_id, PENDING_FILE) or self.find_vouch_by_id(vouch_id, VERIFICATION_FILE)
            if vouch:
                self.move_vouch(vouch, APPROVED_FILE, "Approved")
                await self.log_action(ctx, vouch, "Approved")
                await self.notify_user(vouch["recipient"]["id"], "Vouch Notification", f"Your vouch with the ID `{vouch_id}` has been approved!")
                approved_vouches.append(vouch_id)

        if approved_vouches:
            await ctx.send(f"Vouch IDs {', '.join(map(str, approved_vouches))} have been **approved**.", delete_after=5)

    @commands.command()
    @commands.has_role(VERIFIER_ROLE)
    async def deny(self, ctx, *vouch_ids: int):
        """Deny multiple pending or manual verification vouches."""
        if not vouch_ids:
            return await ctx.send("You need to specify vouch IDs.")

        denied_vouches = []
        for vouch_id in vouch_ids:
            vouch = self.find_vouch_by_id(vouch_id, PENDING_FILE) or self.find_vouch_by_id(vouch_id, VERIFICATION_FILE)
            if vouch:
                self.move_vouch(vouch, DENIED_FILE, "Denied")
                await self.log_action(ctx, vouch, "Denied")
                await self.notify_user(vouch["recipient"]["id"], "Vouch Notification", f"Your vouch with the ID `{vouch_id}` has been denied.")
                denied_vouches.append(vouch_id)

        if denied_vouches:
            await ctx.send(f"Vouch IDs {', '.join(map(str, denied_vouches))} have been **denied**.", delete_after=5)

    @commands.command()
    @commands.has_role(ADMIN_OVERRIDE_ROLE)
    async def forceapprove(self, ctx, vouch_id: int):
        """Force approve a vouch (admin override)."""
        vouch = self.find_vouch_by_id(vouch_id, PENDING_FILE) or self.find_vouch_by_id(vouch_id, VERIFICATION_FILE)

        if not vouch:
            return await ctx.send("Vouch not found or already processed.")

        self.move_vouch(vouch, APPROVED_FILE, "Approved")
        await self.log_action(ctx, vouch, "Approved (Forced)")
        await self.notify_user(vouch["recipient"]["id"], "Vouch Approved (Admin Override)", f"Your vouch (ID: `{vouch_id}`) has been approved by an administrator.")

        await ctx.send(f"Vouch ID `{vouch_id}` has been **force approved**.", delete_after=5)

    @approve.error
    @deny.error
    @forceapprove.error
    async def verify_error(self, ctx, error):
        """Error handling for verification commands."""
        if isinstance(error, commands.MissingRole):
            await ctx.send("You don't have permission to use this command.")


    @commands.command(aliases=['a'])
    @commands.has_role(VERIFIER_ROLE)
    async def approve_alias(self, ctx, *vouch_ids: int):
        await self.approve(ctx, *vouch_ids)

    @commands.command(aliases=['d'])
    @commands.has_role(VERIFIER_ROLE)
    async def deny_alias(self, ctx, *vouch_ids: int):
        await self.deny(ctx, *vouch_ids)

async def setup(bot):
    await bot.add_cog(VouchVerify(bot))