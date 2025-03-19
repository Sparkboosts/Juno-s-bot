import discord
from discord.ext import commands

BOT_INVITE_URL = "https://discord.com/oauth2/authorize?client_id=1345347442484445245&permissions=265280&scope=bot"
SUPPORT_SERVER = "https://discord.gg/RepiX"

class HelpDropdown(discord.ui.Select):
    def __init__(self, author):
        self.author = author
        options = [
            discord.SelectOption(label="Vouch", emoji="<:emoji_57:1344915683242283068>", description="View vouch-related commands."),
            discord.SelectOption(label="General", emoji="<:black_home:1344915341524074546>", description="View general bot commands."),
            discord.SelectOption(label="Extra", emoji="<:black_BOT:1344915542913454141>", description="View extra commands."),
        ]
        super().__init__(placeholder="Choose a module to view commands", options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            return await interaction.response.send_message("You cannot interact with this menu.", ephemeral=True)

        if self.values[0] == "Vouch":
            embed = discord.Embed(
                title="<:emoji_57:1344915683242283068> Vouch Module",
                description=(
                    "**Commands:**\n"
                    "`profile`, `vouch`, `rep`, `product`, `search`, `status`, `shop`, `image`, `color`, `token`"
                ),
                color=discord.Color.dark_blue()
            )

        elif self.values[0] == "General":
            embed = discord.Embed(
                title="<:black_home:1344915341524074546> General Module",
                description="**Commands:**\n`uptime`, `invite`, `ping`",
                color=discord.Color.dark_blue()
            )

        elif self.values[0] == "Extra":
            embed = discord.Embed(
                title="<:black_BOT:1344915542913454141> Extra Module",
                description="**Commands:**\n`mypending`, `hot`, `top`, `badges`",
                color=discord.Color.dark_blue()
            )

        embed.set_footer(text=self.author.name, icon_url=self.author.display_avatar.url)
        await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):
    def __init__(self, author):
        super().__init__(timeout=60)
        self.add_item(HelpDropdown(author))


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, module: str = None):
        if module:
            module = module.lower()
            if module == "vouch":
                embed = discord.Embed(
                    title="<:emoji_57:1344915683242283068> Vouch Module",
                    description=(
                        "**Commands:**\n"
                        "• `+profile` - View user profile.\n"
                        "• `+vouch` - Manage vouches.\n"
                        "• `+rep` - Give a vouch to someone.\n"
                        "• `+product` - Set your products.\n"
                        "• `+search` - Search vouches.\n"
                        "• `+status` - Check your vouch status.\n"
                        "• `+shop` - Set your shop link.\n"
                        "• `+image` - set thumbnail in profile.\n"
                        "• `+color` - Customize your profile color.\n"
                        "• `+token` - Sends your vouch token in DMs."
                    ),
                    color=discord.Color.dark_blue()
                )

            elif module == "general":
                embed = discord.Embed(
                    title="<:black_home:1344915341524074546> General Module",
                    description=(
                        "**Commands:**\n"
                        "• `+uptime` - Check bot uptime.\n"
                        "• `+invite` - Get the bot invite link.\n"
                        "• `+ping` - Check bot latency."
                    ),
                    color=discord.Color.dark_blue()
                )

            elif module == "extra":
                embed = discord.Embed(
                    title="<:black_BOT:1344915542913454141> Extra Module",
                    description=(
                        "**Commands:**\n"
                        "• `+mypending` - View your pending vouches.\n"
                        "• `+hot` - See the hottest users.\n"
                        "• `+top` - Check the top vouch holders.\n"
                        "• `+badges` - View available badges."
                    ),
                    color=discord.Color.dark_blue()
                )

            else:
                return await ctx.reply("Invalid module! Available modules: `vouch`, `general`, `extra`", delete_after=10)

            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            return await ctx.reply(embed=embed, delete_after=60)

        total_commands = len(self.bot.commands)

        embed = discord.Embed(
            title="Help Menu",
            description=(
                "• Global prefix: `+`\n"
                f"• Total commands: `{total_commands}`\n"
                f"• [Invite Me]({BOT_INVITE_URL})\n"
                "• Use `+help <module>` for more info\n\n"
                "**Modules:**\n"
                "<:emoji_57:1344915683242283068> Vouch\n"
                "<:black_home:1344915341524074546> General\n"
                "<:black_BOT:1344915542913454141> Extra"
            ),
            color=discord.Color.dark_blue()
        )

        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)

        await ctx.reply(content=SUPPORT_SERVER, embed=embed, view=HelpView(ctx.author), delete_after=500)

async def setup(bot):
    await bot.add_cog(Help(bot))