import discord
from discord.ext import commands, tasks

class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.statuses = [
            discord.Game(name=".gg/repiX"),  
            discord.Activity(type=discord.ActivityType.watching, name=".gg/RepiX"),  # Watching status
            discord.Activity(type=discord.ActivityType.listening, name="+help & +invite")  # Listening status
        ]
        self.current_index = 0
        self.status_cycle.start()  

    def cog_unload(self):
        self.status_cycle.cancel()  

    @tasks.loop(seconds=15)
    async def status_cycle(self):
        
        await self.bot.change_presence(activity=self.statuses[self.current_index])
        self.current_index = (self.current_index + 1) % len(self.statuses)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"StatusCog loaded as {self.bot.user}")

async def setup(bot):
    await bot.add_cog(StatusCog(bot))