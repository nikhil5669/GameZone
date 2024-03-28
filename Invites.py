import discord
from discord.ext import commands
import sqlite3

class Invites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('invites.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS invite_counts (
                              user_id TEXT PRIMARY KEY,
                              fake_invites INTEGER DEFAULT 0,
                              left_invites INTEGER DEFAULT 0,
                              current_invites INTEGER DEFAULT 1
                          )''')
        self.conn.commit()

    async def update_invite_counts(self, guild):
        invites = await guild.invites()
        for invite in invites:
            inviter_id = invite.inviter.id
            fake_invites = 0
            left_invites = 0
            current_invites = invite.uses
            self.cursor.execute('SELECT * FROM invite_counts WHERE user_id=?', (str(inviter_id),))
            result = self.cursor.fetchone()
            if result:
                fake_invites = result[1]
                left_invites = result[2]
            self.cursor.execute('INSERT OR REPLACE INTO invite_counts (user_id, fake_invites, left_invites, current_invites) VALUES (?, ?, ?, ?)',
                                (str(inviter_id), fake_invites, left_invites, current_invites))
        self.conn.commit()

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            await self.update_invite_counts(guild)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.update_invite_counts(member.guild)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.update_invite_counts(member.guild)

    @commands.command()
    async def invites(self, ctx, member: discord.Member = None):
        """Check how many invites a user has."""
        if member is None:
            member = ctx.author
        self.cursor.execute('SELECT * FROM invite_counts WHERE user_id=?', (str(member.id),))
        result = self.cursor.fetchone()
        if result:
            fake_invites, left_invites, current_invites = result[1], result[2], result[3]
            await ctx.send(f"{member.display_name} has:\n"
                           f"Fake Invites: {fake_invites}\n"
                           f"Left Invites: {left_invites}\n"
                           f"Current Invites: {current_invites}")
        else:
            await ctx.send("No invite data found for this user.")

    @commands.command()
    async def ilb(self, ctx):
        """Display the invite leaderboard."""
        self.cursor.execute('SELECT * FROM invite_counts ORDER BY current_invites DESC LIMIT 10')
        results = self.cursor.fetchall()
        if results:
            leaderboard = "Invite Leaderboard:\n"
            for i, result in enumerate(results, start=1):
                member = ctx.guild.get_member(int(result[0]))
                if member:
                    leaderboard += f"{i}. {member.display_name} - {result[3]} invites\n"
                else:
                    leaderboard += f"{i}. User (ID: {result[0]}) - {result[3]} invites\n"
            await ctx.send(leaderboard)
        else:
            await ctx.send("No invite data found.")

def setup(bot):
    bot.add_cog(Invites(bot))
    