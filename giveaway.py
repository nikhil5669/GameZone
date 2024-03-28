import discord
from discord.ext import commands
import sqlite3
import asyncio
from datetime import datetime, timedelta
import pytz

class GiveawayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('giveaways.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS giveaways
                             (message_id INTEGER PRIMARY KEY, winners INTEGER, end_time INTEGER, participants TEXT, host INTEGER, title TEXT, description TEXT)''')
        self.conn.commit()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        guild = self.bot.get_guild(payload.guild_id)
        
        if payload.emoji.name == '🎉':
            self.cursor.execute("SELECT * FROM giveaways WHERE message_id = ?", (payload.message_id,))
            giveaway = self.cursor.fetchone()
            if giveaway:
                participants = giveaway[3].split(',')
                if str(payload.user_id) not in participants:
                    participants.append(str(payload.user_id))
                    participants_str = ','.join(participants)
                    self.cursor.execute("UPDATE giveaways SET participants = ? WHERE message_id = ?", (participants_str, payload.message_id))
                    self.conn.commit()
                    await self.update_entries(guild, payload.message_id)

    async def update_entries(self, guild, message_id):
        self.cursor.execute("SELECT * FROM giveaways WHERE message_id = ?", (message_id,))
        giveaway = self.cursor.fetchone()
        if giveaway:
            entries = len(giveaway[3].split(','))
            end_time = datetime.fromtimestamp(giveaway[2], pytz.timezone('Asia/Kolkata'))
            end_time_formatted = end_time.strftime("%d/%m/%y %I:%M %p")

            embed = discord.Embed(color=discord.Color.blue(), title=giveaway[5])
            embed.add_field(name="Hosted by", value=guild.get_member(giveaway[4]).mention)
            embed.add_field(name="Winners", value=giveaway[1])
            embed.add_field(name="Ending Time", value=end_time_formatted)
            embed.add_field(name="Entries", value=entries)

            if datetime.now(pytz.timezone('Asia/Kolkata')) > end_time:
                embed.add_field(name="Status", value="Ended")
            else:
                embed.add_field(name="Status", value="Ongoing")

            message_channel = self.bot.get_channel(message_id)
            await message_channel.send(embed=embed)

    @commands.command()
    async def gcreate(self, ctx: commands.Context, winners: int, duration: str, *, title: str):
        """Create a giveaway."""
        duration_seconds = self.parse_duration(duration)
        if duration_seconds <= 0:
            await ctx.send("Invalid duration provided. Please use a valid duration.")
            return

        end_time = datetime.now(pytz.timezone('Asia/Kolkata')) + timedelta(seconds=duration_seconds)
        end_time_formatted = end_time.strftime("%d/%m/%y %I:%M %p")

        embed = discord.Embed(color=discord.Color.blue(), title=title)
        embed.add_field(name="Hosted by", value=ctx.author.mention)
        embed.add_field(name="Winners", value=winners)
        embed.add_field(name="Ending Time", value=end_time_formatted)
        embed.add_field(name="Entries", value="0")
        embed.set_footer(text="React with 🎉 to enter!")

        message = await ctx.send(embed=embed)

        self.cursor.execute("INSERT INTO giveaways (message_id, winners, end_time, participants, host, title) VALUES (?, ?, ?, ?, ?, ?)",
                            (message.id, winners, end_time.timestamp(), "", ctx.author.id, title))
        self.conn.commit()

        await message.add_reaction("🎉")

        await asyncio.sleep(duration_seconds)
        await self.end_giveaway(ctx.guild, message.id)

    async def end_giveaway(self, guild, message_id):
        """End a giveaway."""
        self.cursor.execute("SELECT * FROM giveaways WHERE message_id = ?", (message_id,))
        giveaway = self.cursor.fetchone()
        if giveaway:
            end_time = datetime.fromtimestamp(giveaway[2], pytz.timezone('Asia/Kolkata'))
            end_time_formatted = end_time.strftime("%d/%m/%y %I:%M %p")

            entries = len(giveaway[3].split(','))

            embed = discord.Embed(color=discord.Color.blue(), title=giveaway[5])
            embed.add_field(name="Hosted by", value=guild.get_member(giveaway[4]).mention)
            embed.add_field(name="Winners", value=giveaway[1])
            embed.add_field(name="Ending Time", value=end_time_formatted)
            embed.add_field(name="Entries", value=entries)
            embed.add_field(name="Status", value="Ended")

            message_channel = self.bot.get_channel(message_id)
            await message_channel.send(embed=embed)

            self.cursor.execute("DELETE FROM giveaways WHERE message_id = ?", (message_id,))
            self.conn.commit()

    def parse_duration(self, duration: str):
        if duration.endswith("s"):
            return int(duration[:-1])
        elif duration.endswith("m"):
            return int(duration[:-1]) * 60
        elif duration.endswith("h"):
            return int(duration[:-1]) * 60 * 60
        elif duration.endswith("d"):
            return int(duration[:-1]) * 24 * 60 * 60
def setup(bot):
    bot.add_cog(GiveawayCog(bot))            