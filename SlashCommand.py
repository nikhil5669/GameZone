import discord
from discord.ext import commands
import asyncio

class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx):
        await ctx.send("Hello, world!")

class SlashCommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def make_slash(self, ctx, command_name: str, *, description: str = "No description"):
        """
        Convert an existing command into a slash command.

        Parameters:
        - command_name (str): The name of the command to convert.
        - description (str): The description of the new slash command (optional).
        """
        command = self.bot.get_command(command_name)
        if not command:
            return await ctx.send(f"Command `{command_name}` not found.")

        # Check if the command's callback is a coroutine function
        if not asyncio.iscoroutinefunction(command.callback):
            return await ctx.send(f"Command `{command_name}` is not a coroutine command.")

        options = []
        for param in command.clean_params.values():
            if isinstance(param.annotation, bool):
                option_type = 5  # Boolean option type
            elif param.annotation == str:
                option_type = 3  # String option type
            elif param.annotation in (int, float):
                option_type = 4  # Integer option type
            else:
                return await ctx.send(f"Unsupported parameter type for command `{command_name}`.")

            options.append({
                "type": option_type,
                "name": param.name,
                "description": param.name.capitalize(),
                "required": param.default == param.empty  # Set required to True if parameter doesn't have a default value
            })

        guild_id = ctx.guild.id
        command_data = {
            "name": command_name,
            "description": description,
            "options": options
        }

        # Use bot.http to interact with Discord API directly
        await self.bot.http.request(discord.http.Route('POST', f'/applications/{self.bot.user.id}/guilds/{guild_id}/commands'), json=command_data)
        await ctx.send(f"Successfully created a slash command for `{command_name}`!")

    async def sync_commands(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for guild in self.bot.guilds:
                commands_to_sync = []
                for command in self.bot.commands:
                    if isinstance(command, commands.Command):
                        if asyncio.iscoroutinefunction(command.callback):
                            options = []
                            for param in command.clean_params.values():
                                if isinstance(param.annotation, bool):
                                    option_type = 5  # Boolean option type
                                elif param.annotation == str:
                                    option_type = 3  # String option type
                                elif param.annotation in (int, float):
                                    option_type = 4  # Integer option type
                                else:
                                    return await ctx.send(f"Unsupported parameter type for command `{command_name}`.")

                                options.append({
                                    "type": option_type,
                                    "name": param.name,
                                    "description": param.name.capitalize(),
                                    "required": param.default == param.empty  # Set required to True if parameter doesn't have a default value
                                })

                            command_data = {
                                "name": command.name,
                                "description": command.help or "No description",
                                "options": options
                            }
                            commands_to_sync.append(command_data)

                # Use bot.http to interact with Discord API directly
                await self.bot.http.request(discord.http.Route('PUT', f'/applications/{self.bot.user.id}/guilds/{guild.id}/commands'), json=commands_to_sync)
            await asyncio.sleep(3600)  # Sync every hour

def setup(bot):
    cog = TestCog(bot)
    bot.add_cog(cog)
    bot.loop.create_task(cog.sync_commands())

    slash_cog = SlashCommandCog(bot)
    bot.add_cog(slash_cog)
    