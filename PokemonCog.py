import discord
from discord.ext import commands
import requests
import random

class PokemonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_base_url = "https://pokeapi.co/api/v2"

    @commands.command()
    async def encounter_pokemon(self, ctx):
        """
        Encounter a wild Pokémon.
        """
        # Fetch a random Pokémon species
        pokemon_id = random.randint(1, 898)  # There are 898 Pokémon in total
        pokemon_data = self.get_pokemon_data(pokemon_id)

        # Display the encountered Pokémon
        if pokemon_data:
            await ctx.send(f"A wild {pokemon_data['name']} appeared!")

    def get_pokemon_data(self, pokemon_id):
        """
        Retrieve data for a Pokémon from the PokéAPI.
        """
        try:
            response = requests.get(f"{self.api_base_url}/pokemon/{pokemon_id}")
            if response.status_code == 200:
                pokemon_data = response.json()
                return pokemon_data
            else:
                print(f"Failed to fetch Pokémon data. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

def setup(bot):
    bot.add_cog(PokemonCog(bot))
