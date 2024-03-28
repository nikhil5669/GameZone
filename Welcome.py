import discord
from discord.ext import commands
import sqlite3

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('welcome_leave.db')  # Connect to the database
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS welcome_leave_channels (
                              guild_id TEXT PRIMARY KEY,
                              welcome_channel_id TEXT,
                              leave_channel_id TEXT
                          )''')
        self.conn.commit()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Retrieve the welcome channel ID from the database
        self.cursor.execute('SELECT welcome_channel_id FROM welcome_leave_channels WHERE guild_id=?', (str(member.guild.id),))
        result = self.cursor.fetchone()
        welcome_channel_id = result[0] if result else None

        if welcome_channel_id:
            welcome_channel = member.guild.get_channel(int(welcome_channel_id))
            if welcome_channel:
                # Construct a professional welcome message
                welcome_message = (
                    f"**Welcome to {member.guild.name}, {member.display_name}!**\n\n"
                    f"We're thrilled to have you join us.\n\n"
                    f"Please take a moment to read the server rules in {welcome_channel.mention}.\n\n"
                    f"If you have any questions, feel free to ask in the appropriate channels.\n\n"
                    f"Enjoy your time here!\n\n"
                    f"ℹ️ **Server Information:**\n"
                    f"• **Members:** {member.guild.member_count}\n"
                    f"• **Created:** {member.guild.created_at.strftime('%Y-%m-%d')}"
                )
                # Send the welcome message in a professional format
                guild_icon_url = member.guild.icon.url if member.guild.icon else discord.Embed.Empty
                embed = discord.Embed(title=f"👋 Welcome, {member.display_name}!", description=welcome_message, color=0x42f4f4)
                embed.set_thumbnail(url=guild_icon_url)
                await welcome_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # Retrieve the leave channel ID from the database
        self.cursor.execute('SELECT leave_channel_id FROM welcome_leave_channels WHERE guild_id=?', (str(member.guild.id),))
        result = self.cursor.fetchone()
        leave_channel_id = result[0] if result else None

        if leave_channel_id:
            leave_channel = member.guild.get_channel(int(leave_channel_id))
            if leave_channel:
                # Construct a professional leave message
                leave_message = f"**Goodbye, {member.name}!** 👋 We'll miss you!"

                # Send the leave message in a professional format
                embed = discord.Embed(title="Goodbye!", description=leave_message, color=0xff5733)
                await leave_channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_welcome_channel(self, ctx, channel: discord.TextChannel):
        """Set the welcome channel."""
        self.cursor.execute('INSERT OR REPLACE INTO welcome_leave_channels (guild_id, welcome_channel_id) VALUES (?, ?)', (str(ctx.guild.id), str(channel.id)))
        self.conn.commit()
        await ctx.send(f"Welcome channel set to {channel.mention}.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_leave_channel(self, ctx, channel: discord.TextChannel):
        """Set the leave channel."""
        self.cursor.execute('INSERT OR REPLACE INTO welcome_leave_channels (guild_id, leave_channel_id) VALUES (?, ?)', (str(ctx.guild.id), str(channel.id)))
        self.conn.commit()
        await ctx.send(f"Leave channel set to {channel.mention}.")

    @commands.command()
    async def testwelcome(self, ctx):
        """Simulate a member joining and send a test welcome message."""
        # Retrieve the welcome channel ID from the database
        self.cursor.execute('SELECT welcome_channel_id FROM welcome_leave_channels WHERE guild_id=?', (str(ctx.guild.id),))
        result = self.cursor.fetchone()
        welcome_channel_id = result[0] if result else None

        if welcome_channel_id:
            welcome_channel = ctx.guild.get_channel(int(welcome_channel_id))
            if welcome_channel:
                # Construct a professional welcome message for testing
                welcome_message = (
                    f"**Welcome to {ctx.guild.name}, {ctx.author.display_name}!**\n\n"
                    f"We're thrilled to have you join us.\n\n"
                    f"Please take a moment to read the server rules in {welcome_channel.mention}.\n\n"
                    f"If you have any questions, feel free to ask in the appropriate channels.\n\n"
                    f"Enjoy your time here!\n\n"
                    f"ℹ️ **Server Information:**\n"
                    f"• **Members:** {ctx.guild.member_count}\n"
                    f"• **Created:** {ctx.guild.created_at.strftime('%Y-%m-%d')}"
                )
                # Send the test welcome message in a professional format
                guild_icon_url = ctx.guild.icon.url if ctx.guild.icon else discord.Embed.Empty
                embed = discord.Embed(title=f"👋 Welcome, {ctx.author.display_name}!", description=welcome_message, color=0x42f4f4)
                embed.set_thumbnail(url=guild_icon_url)
                await welcome_channel.send(embed=embed)
        else:
            await ctx.send("Welcome channel is not set. Please set the welcome channel first.")

    @set_welcome_channel.error
    async def set_welcome_channel_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You need to have administrator permissions to use this command.")

    @set_leave_channel.error
    async def set_leave_channel_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You need to have administrator permissions to use this command.")

def setup(bot):
    bot.add_cog(Welcome(bot))
