import discord
from discord.ext import commands
import sqlite3
from cryptography.fernet import Fernet

class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('tickets.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tickets (
                              ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                              user_id INTEGER,
                              ticket_type TEXT,
                              encrypted_data TEXT,
                              open BOOLEAN,
                              channel_id INTEGER
                          )''')
        self.conn.commit()
        self.key = Fernet.generate_key()
        self.fernet = Fernet(self.key)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        if str(payload.emoji) == '❌':
            ticket_channel = self.bot.get_channel(payload.channel_id)
            if ticket_channel:
                await ticket_channel.delete()
                user_id = payload.user_id
                self.cursor.execute('UPDATE tickets SET open = ? WHERE user_id = ?', (False, user_id))
                self.conn.commit()

    @commands.command(aliases=['tp'])
    async def ticketpanel(self, ctx):
        """Display a professional ticket panel with different types of tickets."""
        embed = discord.Embed(title="Ticket Panel", description="Please select a ticket type:", color=discord.Color.blue())
        embed.add_field(name="General Inquiry", value="!openticket general", inline=False)
        embed.add_field(name="Giveaway Assistance", value="!openticket giveaway", inline=False)
        embed.add_field(name="Report an Issue", value="!openticket report", inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=['ot'])
    async def openticket(self, ctx, ticket_type: str):
        """Open a new ticket."""
        ticket_types = {
            'general': 'General Inquiry',
            'giveaway': 'Giveaway Assistance',
            'report': 'Report an Issue'
        }
        if ticket_type not in ticket_types:
            await ctx.send("Invalid ticket type. Please select from available options.")
            return

        user_id = ctx.author.id
        open_ticket = self.get_open_ticket(user_id)
        if open_ticket:
            await ctx.send("You already have an open ticket.")
            return

        # Encrypt the ticket type
        encrypted_ticket_type = self.fernet.encrypt(ticket_types[ticket_type].encode()).decode()[:96]  # Limit to 96 characters

        ticket_data = f"User ID: {user_id}\nTicket Type: {encrypted_ticket_type}"
        encrypted_data = self.fernet.encrypt(ticket_data.encode()).decode()

        # Create a ticket channel with encrypted ticket type as the channel name
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        # Ensure the channel name doesn't exceed 100 characters
        channel_name = f"-ticket-{encrypted_ticket_type}"
        channel_name = channel_name[:99]  # Limit to 99 characters to leave space for potential suffix
        ticket_channel = await ctx.guild.create_text_channel(name=channel_name, overwrites=overwrites)

        # Send a message with a reaction to close the ticket
        ticket_message = await ticket_channel.send(f"Ticket Type: {ticket_types[ticket_type]}\nReact with ❌ to close this ticket.")

        # Add reaction to close the ticket
        await ticket_message.add_reaction('❌')

        # Store ticket information in the database
        self.cursor.execute('INSERT INTO tickets (user_id, ticket_type, encrypted_data, open, channel_id) VALUES (?, ?, ?, ?, ?)',
                            (user_id, encrypted_ticket_type, encrypted_data, True, ticket_channel.id))
        self.conn.commit()

        await ctx.send(f"Successfully created {ticket_types[ticket_type]} ticket in {ticket_channel.mention}. A support staff member will assist you shortly.")

        # Delete the command message
        await ctx.message.delete()

    @commands.command(aliases=['ct'])
    async def closeticket(self, ctx):
        """Close the current ticket."""
        user_id = ctx.author.id
        open_ticket = self.get_open_ticket(user_id)
        if not open_ticket:
            await ctx.send("You don't have any open tickets.")
            return

        ticket_channel = ctx.guild.get_channel(open_ticket[5])
        if ticket_channel:
            await ticket_channel.delete()

        self.cursor.execute('UPDATE tickets SET open = ? WHERE user_id = ?', (False, user_id))
        self.conn.commit()
        await ctx.send("Your ticket has been closed. If you need further assistance, feel free to open a new ticket.")

    @commands.command(aliases=['fct'])
    @commands.has_permissions(administrator=True)
    async def forcecloseticket(self, ctx, user: discord.User):
        """Force close a ticket for a specific user."""
        open_ticket = self.get_open_ticket(user.id)
        if not open_ticket:
            await ctx.send("The specified user doesn't have any open tickets.")
            return
        
        ticket_channel = ctx.guild.get_channel(open_ticket[5])
        if ticket_channel:
            await ticket_channel.delete()

        self.cursor.execute('UPDATE tickets SET open = ? WHERE user_id = ?', (False, user.id))
        self.conn.commit()
        await ctx.send(f"Ticket closed successfully for {user.mention}.")

    @commands.command(aliases=['ti'])
    async def ticketinfo(self, ctx):
        """Display information about the user's open ticket."""
        user_id = ctx.author.id
        open_ticket = self.get_open_ticket(user_id)
        if open_ticket:
            decrypted_ticket_type = self.fernet.decrypt(open_ticket[2].encode()).decode()
            decrypted_ticket_data = self.fernet.decrypt(open_ticket[3].encode()).decode()
            embed = discord.Embed(title="Open Ticket Information", color=discord.Color.green())
            embed.add_field(name="Ticket Type", value=decrypted_ticket_type)
            embed.add_field(name="Ticket Data", value=decrypted_ticket_data)
            await ctx.send(embed=embed)
        else:
            await ctx.send("You don't have any open tickets.")

    @commands.command(aliases=['th'])
    async def tickethelp(self, ctx):
        """Display help information for ticket commands."""
        embed = discord.Embed(title="Ticket System Help", color=discord.Color.blue())
        embed.add_field(name="Ticket Panel", value="Display available ticket types and their corresponding commands.", inline=False)
        embed.add_field(name="Open Ticket", value="Open a new ticket with the specified type.", inline=False)
        embed.add_field(name="Close Ticket", value="Close the current ticket.", inline=False)
        embed.add_field(name="Force Close Ticket", value="Force close a ticket for a specific user (admin only).", inline=False)
        embed.add_field(name="Ticket Info", value="Display information about the user's open ticket.", inline=False)
        await ctx.send(embed=embed)

    def get_open_ticket(self, user_id):
        """Get the open ticket for a user."""
        self.cursor.execute('SELECT * FROM tickets WHERE user_id = ? AND open = ?', (user_id, True))
        return self.cursor.fetchone()

def setup(bot):
    bot.add_cog(TicketCog(bot))
  
        