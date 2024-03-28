import discord
from discord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        """
        Display help information for all commands.
        """
        embed = discord.Embed(
            title="Command Help",
            description="Here are all available commands:",
            color=0x7289da  # Discord color
        )
        embed.set_thumbnail(url="https://i.imgur.com/yDxQw6a.png")  # Discord logo

        for cog in self.bot.cogs:
            if cog.lower() not in ["moderation", "welcome"]:
                cog_commands = []
                for command in self.bot.get_cog(cog).get_commands():
                    if not command.hidden:
                        cog_commands.append(f"• `{command.name}` - {command.help}")
                if cog_commands:
                    embed.add_field(name=cog.replace("Cog", "").replace("Funcog", "Fun Commands"), value="\n".join(cog_commands), inline=False)

        embed.set_footer(text="Use !help [command] for more info on a command.")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(HelpCog(bot))
  