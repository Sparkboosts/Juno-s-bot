import discord
from discord.ext import commands
import json
from datetime import datetime
import aiohttp

PROFILE_FILE = "profile.json"
APPROVED_FILE = "approved.json"
SCAMMER_FILE = "scammer.json"

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_data(self, filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return [] if filename == APPROVED_FILE else {}

    def save_data(self, filename, data):
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def load_profile(self):
        return self.load_data(PROFILE_FILE)

    def save_profile(self, data):
        self.save_data(PROFILE_FILE, data)

    def load_scammers(self):
        return self.load_data(SCAMMER_FILE)

    def get_user_vouch_info(self, user_id):
        approved_vouches = self.load_data(APPROVED_FILE)

        if not isinstance(approved_vouches, list):
            return 0, [], []

        user_vouches = [
            v for v in approved_vouches
            if v.get("recipient", {}).get("id") == user_id and v.get("status") == "Approved"
        ]

        last_comments = [v.get("comment", "No comment provided") for v in user_vouches[-5:]]

        return len(user_vouches), last_comments, user_vouches

    async def get_scammer_embed(self, member, reason):
        embed = discord.Embed(
            title=f"`{member.display_name}` IS A SCAMMER",
            description="**MARKED BY STAFF**",
            color=0xFF0000
        )
        embed.add_field(name="**This user was Marked For:**", value=reason, inline=False)

        embed.set_footer(text="Created by flash | .gg/sex")
        return embed

    async def profile_embed(self, member):
        scammers = self.load_scammers()
        if str(member.id) in scammers:
            reason = scammers[str(member.id)]
            return await self.get_scammer_embed(member, reason)

        positive_vouches, last_comments, all_vouches = self.get_user_vouch_info(member.id)

        profile_data = self.load_profile()
        user_profile = profile_data.get(str(member.id), {
            "colour": "#FFFFFF",
            "shop": "Set this!",
            "product": [],
            "discord": "Set this!",
            "badges": [],
            "image": None
        })

        embed = discord.Embed(
            title=f"{member.display_name}'s Profile",
            color=discord.Color(int(user_profile.get("colour", "#FFFFFF").lstrip("#"), 16))
        )

        embed.add_field(
            name="**__User Information__**",
            value=f"**ID:** {member.id}\n"
                  f"**Registration Date:** {member.created_at.strftime('%Y-%m-%d')}\n"
                  f"**Display Name:** {member.display_name}\n"
                  f"**Mention:** {member.mention}\n"
            f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
            inline=False
        )

        embed.add_field(
            name="**__Vouch Information__**",
            value=f"**Positive:** {positive_vouches}\n"
                  f"**Negative:** 0\n"
                  f"**Imported:** 0\n"
                  f"**Overall:** {positive_vouches}",
            inline=False
        )

        product_list = "\n".join([f"- {p}" for p in user_profile.get('product', [])]) if user_profile.get('product') else "Set this!"
        embed.add_field(
            name="**__User Configuration__**",
            value=f"**Shop:** {user_profile.get('shop', 'Set this!')}\n"
                  f"**Product:** {product_list}\n"
                  f"**Discord:** {user_profile.get('discord', 'Set this!')}",
            inline=False
        )

        BADGE_EMOJIS = {
            "Owner": "<:owner:1344041796929454190>",
            "Developer": "<:dev:1344213763317829733>",
            "Admin": "<:Admin:1344042067013144718>",
            "Staff": "<:StaffAll:1344041942735913185>",
            "Trusted": "<:trusted:1344213932759453749>",
            "Donator": "<:emoji_6:1344042502969098311>",
            "User": "<:mmmeb:1344041566800576586>"
        }

        badge_display = [f"{BADGE_EMOJIS.get(badge, '')} {badge}" for badge in user_profile.get('badges', [])]

        if "User" not in user_profile.get('badges', []):
            badge_display.append(f"{BADGE_EMOJIS['User']} User")

        embed.add_field(
            name="**__Badges__**",
            value="\n".join(badge_display) if badge_display else f"{BADGE_EMOJIS['User']} User",
            inline=False
        )

        embed.add_field(
            name="**__Past 5 Comments__**",
            value="\n".join(last_comments[::-1]) if last_comments else "No vouches yet.",
            inline=False
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        if user_profile.get("image"):
            embed.set_image(url=user_profile["image"])

        embed.set_footer(text="Created by Flash | Juno Jhat")

        return embed

    @commands.command(aliases=["p"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def profile(self, ctx, *, user_input: str = None):
        try:
            if user_input:
                try:
                    # Try to fetch the user by ID, mention, or username
                    member = await commands.UserConverter().convert(ctx, user_input)
                except commands.BadArgument:
                    return await ctx.reply("User not found. Please provide a valid mention, username, or ID.", delete_after=10)
            else:
                member = ctx.author

            embed = await self.profile_embed(member)
            await ctx.reply(embed=embed, delete_after=20)

        except Exception as e:
            print(f"[ERROR] Failed to display profile: {e}")
            await ctx.reply("An error occurred while generating the profile.", delete_after=10)

    @commands.command()
    async def shop(self, ctx, *, shop_link: str = None):
        profile_data = self.load_profile()
        user_profile = profile_data.setdefault(str(ctx.author.id), {})
        user_profile["shop"] = shop_link if shop_link else "Set this!"
        self.save_profile(profile_data)

        await ctx.reply("Your shop has been updated." if shop_link else "Your shop has been reset.", delete_after=20)

    @commands.command()
    async def discord(self, ctx, *, discord_link: str = None):
        profile_data = self.load_profile()
        user_profile = profile_data.setdefault(str(ctx.author.id), {})
        user_profile["discord"] = discord_link if discord_link else "Set this!"
        self.save_profile(profile_data)

        await ctx.reply("Your Discord has been updated." if discord_link else "Your Discord has been reset.", delete_after=20)

    @commands.command()
    async def product(self, ctx, *, product_name: str = None):
        profile_data = self.load_profile()
        user_profile = profile_data.setdefault(str(ctx.author.id), {})
        
        if product_name:
            # Split by commas and strip spaces
            products = [p.strip() for p in product_name.split(",") if p.strip()]
            user_profile["product"] = products
        else:
            user_profile["product"] = []

        self.save_profile(profile_data)

        await ctx.reply("Product updated." if product_name else "Products reset.", delete_after=20)
    @commands.command()
    async def image(self, ctx, url: str = None):
        profile_data = self.load_profile()
        user_profile = profile_data.setdefault(str(ctx.author.id), {})

        user_profile["image"] = url if url else None
        self.save_profile(profile_data)

        await ctx.reply("Image updated." if url else "Image removed.", delete_after=20)

    @commands.command()
    async def colour(self, ctx, hex_color: str = "#FFFFFF"):
        profile_data = self.load_profile()
        user_profile = profile_data.setdefault(str(ctx.author.id), {})
        user_profile["colour"] = hex_color
        self.save_profile(profile_data)

        await ctx.reply(f"Profile colour updated to {hex_color}.", delete_after=20)

async def setup(bot):
    await bot.add_cog(Profile(bot))