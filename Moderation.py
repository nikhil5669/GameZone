import discord
from discord.ext import commands

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Kick a member from the server."""
        await member.kick(reason=reason)
        await ctx.send(f"{member.display_name} has been kicked from the server. Reason: {reason}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def bn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Ban a member from the server."""
        await member.ban(reason=reason)
        await ctx.send(f"{member.display_name} has been banned from the server. Reason: {reason}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        """Unban a member from the server."""
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f"{user.name}#{user.discriminator} has been unbanned.")
                return

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, limit: int):
        """Delete a specified number of messages from the channel."""
        await ctx.channel.purge(limit=limit + 1)  # +1 to include the command message itself
        await ctx.send(f"{limit} messages have been purged.", delete_after=5)

    @commands.command()
    @commands.has_permissions(manage_nicknames=True)
    async def nickname(self, ctx, member: discord.Member, *, new_nickname):
        """Change the nickname of a member."""
        await member.edit(nick=new_nickname)
        await ctx.send(f"Nickname for {member.display_name} has been changed to {new_nickname}")

    @commands.command(aliases=['mohelp'])
    async def mhelp(self, ctx):
        """Display all available moderation commands and their uses."""
        help_message = (
            "**Moderation Commands:**\n"
            "`!kick <member> [reason]`: Kick a member from the server.\n"
            "`!ban <member> [reason]`: Ban a member from the server.\n"
            "`!unban <username#discriminator>`: Unban a member from the server.\n"
            "`!purge <limit>`: Delete a specified number of messages from the channel.\n"
            "`!nickname <member> <new_nickname>`: Change the nickname of a member.\n"
            "Use `!help <command>` for more details on each command."
        )
        await ctx.send(help_message)

def setup(bot):
    bot.add_cog(ModerationCog(bot))
    