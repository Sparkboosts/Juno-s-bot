import discord
from discord.ext import commands, tasks
import json
import os
import random
from datetime import datetime, timedelta


DARK_BLUE = 0x00008B
ERROR_COLOR = 0xFF0000


PENDING_FILE = "pending.json"
BLACKLIST_FILE = "blacklist.json"
VERIFICATION_FILE = "verification.json"
ALLVOUCHES_FILE = "allvouches.json"
USED_IDS_FILE = "used_ids.json"


ERROR_EMOJI = "<:emoji_1:1344015306393255966>"


SUPPORT_SERVER_LINK = "https://discord.gg/your-support-server"


class Vouch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logging_channel_id = 
# staff server vouch logging 


        for file in [PENDING_FILE, BLACKLIST_FILE, VERIFICATION_FILE, ALLVOUCHES_FILE, USED_IDS_FILE]:
            if not os.path.exists(file):
                with open(file, "w") as f:
                    json.dump([], f)

        self.check_pending_verifications.start()

    def load_data(self, file_path):
        with open(file_path, "r") as f:
            return json.load(f)

    def save_data(self, file_path, data):
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    def get_next_vouch_id(self):
        """Generate the next available unique vouch ID."""
        used_ids = set(self.load_data(USED_IDS_FILE))
        next_id = 1
        while next_id in used_ids:
            next_id += 1
        used_ids.add(next_id)
        self.save_data(USED_IDS_FILE, list(used_ids))
        return next_id

    @commands.command(aliases=["vouch"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rep(self, ctx, member: discord.Member = None, *, comment: str = None):
        """Vouch for a user with a comment"""
        giver = ctx.author


        if member is None or comment is None:
            return await self.send_temp_embed(ctx, "Bad Input", f"{ERROR_EMOJI} Use: `+rep <user> <comment>`", ERROR_COLOR)

        recipient = member


        if giver.id == recipient.id:
            return await self.send_temp_embed(ctx, "Error", f"{ERROR_EMOJI} You cannot vouch for yourself!", ERROR_COLOR)
        if recipient.bot:
            return await self.send_temp_embed(ctx, "Error", f"{ERROR_EMOJI} You cannot vouch for a bot!", ERROR_COLOR)


        if (discord.utils.utcnow() - giver.created_at).days < 7:
            return await self.send_temp_embed(ctx, "Error", f"{ERROR_EMOJI} Your account must be at least **7 days old** to vouch.", ERROR_COLOR)


        blacklist_data = self.load_data(BLACKLIST_FILE)
        if str(giver.id) in blacklist_data or str(recipient.id) in blacklist_data:
            return await self.send_temp_embed(ctx, "Error", f"{ERROR_EMOJI} One of the users is blacklisted from vouching.", ERROR_COLOR)


        vouch_id = self.get_next_vouch_id()


        requires_verification = random.randint(1, 7) == 1
        vouch_status = "Manual Verification" if requires_verification else "Pending"


        vouch_entry = {
            "id": vouch_id,
            "recipient": {"id": recipient.id, "tag": str(recipient)},
            "giver": {"id": giver.id, "tag": str(giver)},
            "comment": comment,
            "date": str(datetime.utcnow()),
            "status": vouch_status
        }


        pending_vouches = self.load_data(PENDING_FILE)
        pending_vouches.append(vouch_entry)
        self.save_data(PENDING_FILE, pending_vouches)


        all_vouches = self.load_data(ALLVOUCHES_FILE)
        all_vouches.append(vouch_entry)
        self.save_data(ALLVOUCHES_FILE, all_vouches)


        if requires_verification:
            verification_data = self.load_data(VERIFICATION_FILE)
            verification_data.append({
                "id": vouch_id,
                "recipient": recipient.id,
                "expire_at": str(datetime.utcnow() + timedelta(days=2))
            })
            self.save_data(VERIFICATION_FILE, verification_data)


        confirm_embed = discord.Embed(
            title="Vouch Submitted!",
            description=f"Your vouch for **{recipient}** has been submitted and is awaiting review!",
            color=DARK_BLUE
        )
        confirm_embed.set_footer(text=f"Vouch ID: {vouch_id}")
        await self.send_temp_embed(ctx, embed=confirm_embed)


        log_channel = self.bot.get_channel(self.logging_channel_id)
        if log_channel:
            log_embed = discord.Embed(title=f"Vouch #{vouch_id}", color=0x33F000)
            log_embed.add_field(name="**Recipient:**", value=f"{recipient} | ** Recipient ID:** {recipient.id}", inline=False)
            log_embed.add_field(name="**Giver:**", value=f"{giver} | **Giver ID:** {giver.id}", inline=False)
            log_embed.add_field(name="**Comment:**", value=comment, inline=False)
            log_embed.add_field(name="**Status**", value=f"`{vouch_status}`", inline=False)
            await log_channel.send(embed=log_embed)


        try:
            dm_embed = discord.Embed(
                title="Vouch Notification System",
                description=f"You have received a positive vouch from `{giver}`. The ID of this vouch is `#{vouch_id}`.",
                color=DARK_BLUE
            )
            dm_embed.set_footer(text="Created by flash/Unseen | .gg/Junojhat")
            await recipient.send(embed=dm_embed)
        except discord.Forbidden:
            pass

    @tasks.loop(hours=24)
    async def check_pending_verifications(self):
        """Checks for unverified vouches and denies them after 2 days."""
        now = datetime.utcnow()
        verification_data = self.load_data(VERIFICATION_FILE)

        new_verification_data = []
        for vouch in verification_data:
            expire_time = datetime.fromisoformat(vouch["expire_at"])
            if now >= expire_time:

                recipient = self.bot.get_user(vouch["recipient"])
                if recipient:
                    try:
                        deny_embed = discord.Embed(
                            title="Vouch Denied",
                            description=f"Vouch ID: `#{vouch['id']}` | **Denied due to lack of verification.**",
                            color=ERROR_COLOR
                        )
                        await recipient.send(embed=deny_embed)
                    except discord.Forbidden:
                        pass
            else:
                new_verification_data.append(vouch)

        self.save_data(VERIFICATION_FILE, new_verification_data)

    @rep.error
    async def rep_error(self, ctx, error):
        """Handles command cooldown errors"""
        if isinstance(error, commands.CommandOnCooldown):
            return await self.send_temp_embed(ctx, "Slow Down!", f"{ERROR_EMOJI} You can use this command again in **{error.retry_after:.1f} seconds**.", ERROR_COLOR)

    async def send_temp_embed(self, ctx, title=None, description=None, color=DARK_BLUE, embed=None):
        """Send a temporary embed that deletes after 15 seconds"""
        if embed is None:
            embed = discord.Embed(title=title, description=description, color=color)
        msg = await ctx.send(embed=embed)
        await msg.delete(delay=15)


async def setup(bot):
    await bot.add_cog(Vouch(bot))