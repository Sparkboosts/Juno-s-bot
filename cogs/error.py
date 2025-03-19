import discord
from discord.ext import commands

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="<:crosss:1340612350616539167> Slowdown",
                description="You are using commands too fast, please slow down.",
                color=discord.Color.red()
            )
            await ctx.reply(embed=embed, delete_after=10)

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))