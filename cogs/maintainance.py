import discord
from discord.ext import commands
import json

MAINTENANCE_FILE = "maintenance.json"

class Maintenance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_maintenance()

        
        bot.add_check(self.global_check)

    def load_maintenance(self):
        try:
            with open(MAINTENANCE_FILE, "r") as f:
                self.maintenance_mode = json.load(f).get("maintenance", False)
        except (FileNotFoundError, json.JSONDecodeError):
            self.maintenance_mode = False

    def save_maintenance(self):
        with open(MAINTENANCE_FILE, "w") as f:
            json.dump({"maintenance": self.maintenance_mode}, f, indent=4)

    
    @commands.command()
    @commands.is_owner()
    async def maintenance1start(self, ctx):
        self.maintenance_mode = True
        self.save_maintenance()
        await ctx.send("**Maintenance mode is now enabled. All commands are disabled globally.**")

    
    @commands.command()
    @commands.is_owner()
    async def maintenance1stop(self, ctx):
        self.maintenance_mode = False
        self.save_maintenance()
        await ctx.send("**Maintenance mode is now disabled. All commands are active again.**")

   
    async def global_check(self, ctx):
        
        if ctx.author.id == 1328264744242643059:
            return True

        
        if self.maintenance_mode:
            embed = discord.Embed(
                title="Maintenance Mode Active",
                description="The bot is currently under maintenance. Please try again later | for more info join [Invite Me]({https://discord.gg/TjbyCrHD})",
                color=0x2B2D42
            )
            embed.set_footer(text="Created by UnSeen| RepiX | .gg/repix", icon_url=self.bot.user.avatar.url)
            await ctx.send(embed=embed)
            return False

        return True

async def setup(bot):
    await bot.add_cog(Maintenance(bot))