import discord
from discord.ext import commands
import sqlite3

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        # Connect to the economy database
        with sqlite3.connect('economy.db') as db:
            cursor = db.cursor()

            # Create table if not exists
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                              id INTEGER PRIMARY KEY,
                              name TEXT,
                              level INTEGER,
                              xp INTEGER
                          )''')

            # Check if user exists in database
            cursor.execute("SELECT id FROM users WHERE id = ?", (message.author.id,))
            result = cursor.fetchone()
            if not result:
                # If user does not exist, insert the user
                cursor.execute("INSERT INTO users(id, name, level, xp) VALUES (?, ?, ?, ?)",
                               (message.author.id, message.author.name, 1, 0))
            else:
                # If user exists, increase the xp
                cursor.execute("UPDATE users SET xp = xp + 1 WHERE id = ?", (message.author.id,))

            db.commit()

    @commands.command(aliases=['lehelp', 'levelhelp'])
    async def lhelp(self, ctx):
        """Displays help and instructions for the leveling system."""

        # Introduction and Instructions
        intro = (
            "Welcome to the Leveling System!\n"
            "Earn XP by sending messages and level up to climb the leaderboard!\n\n"
            "**Instructions:**\n"
            "- Use `!profile [user]` or `!prof [user]` to view a user's profile.\n"
            "- Use `!leaderboard` or `!lb` to view the top 10 users on the leaderboard.\n"
            "- Use `!level [user]` to view a user's level.\n"
        )

        # Help Message
        help_message = (
            "**Leveling System Help**\n\n"
            "**Commands:**\n"
            "- `!profile` or `!prof [user]`: View user's profile.\n"
            "- `!leaderboard` or `!lb`: View the top 10 users on the leaderboard.\n"
            "- `!level [user]`: View user's level.\n\n"
            "**Example Usage:**\n"
            "- `!profile @user`: View the specified user's profile.\n"
            "- `!leaderboard`: View the top 10 users on the leaderboard.\n"
            "- `!level @user`: View the specified user's level.\n\n"
            "**Additional Information:**\n"
            "- XP is earned based on the length of your messages.\n"
            "- You can view your own profile using `!profile` without specifying a user.\n"
            "- You can view the leaderboard using `!leaderboard` without specifying a number.\n"
            "- The leveling system is still under development and may be subject to changes in the future.\n\n"
            "If you have any further questions, please feel free to ask."
        )

        # Send the help message as an embed
        embed = discord.Embed(
            title="Leveling System Help",
            description=help_message,
            color=0x00FF00
        )
        await ctx.send(embed=embed)
    @commands.command(aliases=['prof'])
    async def profile(self, ctx, user: discord.Member = None):
        user = user or ctx.author

        # Connect to the economy database
        with sqlite3.connect('economy.db') as db:
            cursor = db.cursor()

            # Get user's data from the database
            cursor.execute("SELECT level, xp FROM users WHERE id = ?", (user.id,))
            result = cursor.fetchone()
            if result:
                level, xp = result
                await ctx.send(f":bar_chart: {user.display_name}'s Profile:\n:sparkles: Level: {level}\n:chart_with_upwards_trend: XP: {xp}")
            else:
                await ctx.send(":x: User not found in the database.")

    @commands.command(aliases=['lb'])
    async def leaderboard(self, ctx):
        # Connect to the economy database
        with sqlite3.connect('economy.db') as db:
            cursor = db.cursor()

            # Get top 10 users based on level
            cursor.execute('SELECT id, level FROM users ORDER BY level DESC LIMIT 10')
            top_users = cursor.fetchall()

            leaderboard = '\n'.join([f"{idx + 1}. {self.bot.get_user(user_id).display_name} (Level: {level})" for idx, (user_id, level) in enumerate(top_users)])
            await ctx.send(f":trophy: Top 10 Users:\n{leaderboard}")

    @commands.command()
    async def level(self, ctx, user: discord.Member = None):
        user = user or ctx.author

        # Connect to the economy database
        with sqlite3.connect('economy.db') as db:
            cursor = db.cursor()

            # Get user's level from the database
            cursor.execute("SELECT level FROM users WHERE id = ?", (user.id,))
            result = cursor.fetchone()
            if result:
                level = result[0]
                await ctx.send(f":sparkles: {user.display_name} is at level {level}.")
            else:
                await ctx.send(":x: User not found in the database.")


        

def setup(bot):
    bot.add_cog(Leveling(bot))
  
        