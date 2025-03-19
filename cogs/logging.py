import discord
from discord.ext import commands
import datetime
import json

WEBHOOK_URLS = {
    "bot_add": "https://discord.com/api/webhooks/1345433279884693555/veC2jDKIJaHL-TBGXkMIKkjNoT2kVZCLyUOdTuoEeferY7ipg0Qp_A4iPjnZwgP0AluC",  
    "bot_remove": "https://discord.com/api/webhooks/1345433472868814888/ufTgkbXNSmX1HmyOTfuhNTxlTkmJ8npC03KBes1v86IJDynTuf2Jm_XgOzxk8E9UXhYm",  
    "server_delete": "https://discord.com/api/webhooks/1340889482957684847/MGGpAnU3p6L4Nz1u_XJ_joo1rLksB-DtyoYM0fkfXJI7a27nts8w-LgzW9ZkYBMu6VYQ",  
    "member_ban": "https://discord.com/api/webhooks/1345433718084341880/Nk9yjBdO29eFQohU5owtimlRr3XZ4rM2H-J191oevLF_5DJ6aBkEm05GGQuDwe8oSmtH",  
    "everyone_ping": "https://discord.com/api/webhooks/1345433940323991562/pNugdMeXuGVT_L95FlzM9QUPk2KuUnjrjrgA2rKpv_FbZdkKGkEcq2dLFJCAHpq79kgW" 

def send_webhook(url, embed):
    """Send a webhook message."""
    if not url:
        return  

    webhook = discord.SyncWebhook.from_url(url)
    webhook.send(embed=embed)


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Log when the bot is added to a server."""
        if not WEBHOOK_URLS["bot_add"]:
            return

        inviter = None
        async for entry in guild.audit_logs(action=discord.AuditLogAction.bot_add, limit=1):
            inviter = entry.user

        embed = discord.Embed(
            title=" RepiX Added to Server!",
            color=0x303136,
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else "")
        embed.add_field(name=" Server Name", value=f"`{guild.name}`", inline=True)
        embed.add_field(name=" Server ID", value=f"`{guild.id}`", inline=True)
        embed.add_field(name=" Created On", value=f"<t:{int(guild.created_at.timestamp())}:F>", inline=True)
        embed.add_field(name=" Total Members Before Leaving", value=f"`{guild.member_count}`", inline=True)
        embed.add_field(name=" Total Roles", value=f"`{len(guild.roles)}`", inline=True)
        embed.add_field(name=" Total Channels", value=f"`{len(guild.channels)}`", inline=True)
        embed.set_footer(text=f"Server ID: {guild.id}")

        send_webhook(WEBHOOK_URLS["bot_add"], embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """Log when the bot is removed from a server."""
        if not WEBHOOK_URLS["bot_remove"]:
            return

        embed = discord.Embed(
            title="RepiX Removed from Server!",
            color=0x303136,
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else "")
        embed.add_field(name=" Server Name", value=f"`{guild.name}`", inline=True)
        embed.add_field(name=" Server ID", value=f"`{guild.id}`", inline=True)
        embed.add_field(name=" Created On", value=f"<t:{int(guild.created_at.timestamp())}:F>", inline=True)
        embed.add_field(name=" Total Members Before Leaving", value=f"`{guild.member_count}`", inline=True)
        embed.add_field(name=" Total Roles", value=f"`{len(guild.roles)}`", inline=True)
        embed.add_field(name=" Total Channels", value=f"`{len(guild.channels)}`", inline=True)
        embed.set_footer(text=f"Server ID: {guild.id}")

        send_webhook(WEBHOOK_URLS["bot_remove"], embed)

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        """Log when a server is deleted."""
        if not WEBHOOK_URLS["server_delete"]:
            return

        if before and after is None:
            embed = discord.Embed(
                title="Server Deleted!",
                color=0x303136,
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_thumbnail(url=before.icon.url if before.icon else "")
            embed.add_field(name=" Server Name", value=f"`{before.name}`", inline=True)
            embed.add_field(name=" Server ID", value=f"`{before.id}`", inline=True)
            embed.add_field(name=" Created On", value=f"<t:{int(before.created_at.timestamp())}:F>", inline=True)
            embed.set_footer(text=f"Server ID: {before.id}")

            send_webhook(WEBHOOK_URLS["server_delete"], embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """Log when a member is banned."""
        if not WEBHOOK_URLS["member_ban"]:
            return

        embed = discord.Embed(
            title="Member Banned!",
            color=0x303136,
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name=" User", value=f"{user.mention} (`{user.id}`)", inline=False)
        embed.add_field(name=" Server", value=f"`{guild.name}`", inline=True)
        embed.set_footer(text=f"Server ID: {guild.id}")

        send_webhook(WEBHOOK_URLS["member_ban"], embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Log @everyone and @here pings."""
        if not WEBHOOK_URLS["everyone_ping"]:
            return

        if message.mention_everyone and not message.author.bot:
            embed = discord.Embed(
                title="Everyone Ping Detected!",
                color=0x303136,
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_author(name=message.author, icon_url=message.author.display_avatar.url)
            embed.add_field(name=" User", value=f"{message.author.mention} (`{message.author.id}`)", inline=False)
            embed.add_field(name=" Server", value=f"`{message.guild.name}`", inline=True)
            embed.add_field(name=" Channel", value=f"{message.channel.mention}", inline=True)
            embed.add_field(name=" Message", value=f"```{message.content}```", inline=False)
            embed.set_footer(text=f"Server ID: {message.guild.id}")

            send_webhook(WEBHOOK_URLS["everyone_ping"], embed)


async def setup(bot):
    await bot.add_cog(Logging(bot))