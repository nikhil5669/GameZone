import discord
from discord.ext import commands
import sqlite3
from collections import defaultdict

class CountingCog(commands.Cog):
    """
    A Discord cog for counting game functionality.
    """
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('counting.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS counting_data
                             (guild_id INTEGER PRIMARY KEY, channel_id INTEGER, count INTEGER)''')
        self.conn.commit()

        self.counting_channels = defaultdict(dict)  # Store counting channel for each guild
        self.last_counter = defaultdict(dict)  # Store last counter for each counting channel

        # Load counting channels from database on cog initialization
        self.load_counting_channels()

    def load_counting_channels(self):
        """
        Load counting channels from the database.
        """
        self.cursor.execute("SELECT guild_id, channel_id, count FROM counting_data")
        rows = self.cursor.fetchall()
        for row in rows:
            guild_id, channel_id, count = row
            self.counting_channels[guild_id] = {"channel_id": channel_id, "count": count}

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Listen for messages and handle counting game logic.
        """
        if message.author.bot:
            return

        if message.guild.id in self.counting_channels:
            counting_channel = self.counting_channels[message.guild.id]
            if message.channel.id == counting_channel["channel_id"]:
                if message.content.isdigit():
                    number = int(message.content)
                    last_count = counting_channel["count"]
                    expected_count = last_count + 1

                    if number == expected_count and message.author != self.last_counter.get(message.guild.id):
                        # Update the count and store the last counter
                        counting_channel["count"] = expected_count
                        self.last_counter[message.guild.id] = message.author

                        # Add reaction to indicate correct count
                        await message.add_reaction("✅")
                    else:
                        # Reset the count and inform the user
                        counting_channel["count"] = 0
                        self.last_counter[message.guild.id] = None  # Clear last counter
                        await message.channel.send(f"Oops! {message.author.mention}, you entered the wrong number or counted consecutively. Count reset to 0. Please start again.")
                else:
                    # Reset the count if the message content is not a number
                    counting_channel["count"] = 0

    @commands.command()
    async def set_counting_channel(self, ctx, channel: discord.TextChannel):
        """
        Set the counting channel.
        """
        try:
            self.cursor.execute("INSERT OR REPLACE INTO counting_data (guild_id, channel_id, count) VALUES (?, ?, 1)",
                                (ctx.guild.id, channel.id))
            self.conn.commit()
            self.counting_channels[ctx.guild.id] = {"channel_id": channel.id, "count": 0}
            await ctx.send(f":white_check_mark: Counting channel successfully set to {channel.mention}. Let's start counting!")
        except sqlite3.Error as e:
            await ctx.send(f":x: An error occurred while setting the counting channel: {e}")

    @commands.command()
    async def chelp(self, ctx):
        """
        Display counting instructions.
        """
        embed = discord.Embed(
            title="Counting Instructions",
            description="Welcome to the counting game! Here are the rules:\n\n"
                        "1️⃣ Count one number at a time.\n"
                        "2️⃣ Do not count out of sequence.\n"
                        "3️⃣ Wait for another user to count before counting again.\n\n"
                        "Let's count together!",
            color=0xFFD700  # Gold color
        )
        await ctx.send(embed=embed)

    def __del__(self):
        """
        Destructor to ensure the database connection is closed.
        """
        self.conn.close()

def setup(bot):
    bot.add_cog(CountingCog(bot))
    