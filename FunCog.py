import discord
from discord.ext import commands
import asyncio
import random
import string
import pyjokes

class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_progress_bar(self, ctx, progress, total):
        bar_length = 20
        progress_length = int((progress / total) * bar_length)
        filled_bar = '█' * progress_length
        empty_bar = '░' * (bar_length - progress_length)
        progress_bar = f'```css\n[{filled_bar}{empty_bar}] ({progress}/{total})\n```'
        embed = discord.Embed(description=progress_bar, color=discord.Color.gold())
        await ctx.send(embed=embed)

    @commands.command(name='hack')
    async def hack_command(self, ctx, user: discord.User):
        """
        Simulate hacking into a user's account.
        """
        # List of hacking stages with corresponding messages and durations
        hacking_stages = [
            ("Identifying target system...", 3),
            ("Gathering reconnaissance data...", 3),
            ("Analyzing network vulnerabilities...", 4),
            ("Creating exploit payloads...", 3),
            ("Deploying backdoor Trojan...", 2),
            ("Initiating brute-force attack...", 5),
            ("Cracking encryption algorithms...", 4),
            ("Escalating privileges...", 2),
            ("Bypassing intrusion detection...", 3),
            ("Executing remote code execution...", 4),
            ("Extracting sensitive information...", 3),
            ("Planting false flags...", 2),
            ("Covering tracks...", 3),
            ("Hacking complete! Access granted.", 0)
        ]

        # Generate email and password based on the provided username
        email = ''.join(random.choices(string.ascii_lowercase, k=8)) + '@example.com'
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        # Send each stage message sequentially with a delay and progress bar
        for i, (message, delay) in enumerate(hacking_stages, 1):
            await ctx.send(f'Progress: {i}/{len(hacking_stages)} - {message}')
            await self.send_progress_bar(ctx, i, len(hacking_stages))
            if delay > 0:
                await asyncio.sleep(delay)

        # Send email and password
        embed = discord.Embed(description=f'Email: `{email}`\nPassword: `{password}`', color=discord.Color.gold())
        await ctx.send(embed=embed)

        # Send "Hacked successfully" message after hacking is completed
        await ctx.send(f'Hacked {user} successfully!')

    @commands.command(name='joke')
    async def joke_command(self, ctx):
        """
        Get a random joke.
        """
        joke = pyjokes.get_joke()
        embed = discord.Embed(
            title="Here's a Joke for You!",
            description=joke,
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(FunCog(bot))
    