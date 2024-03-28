import os
import random
import discord
from discord.ext import commands
from discord.ext.commands import Context
import requests
import asyncio
from help import HelpCog
from economy_cog import Economy 
from level_cog import Leveling
from giveaway import GiveawayCog
from SlashCommand import SlashCommandCog
from PokemonCog import PokemonCog
from FunCog import FunCog
from Counting import CountingCog
from discord import Interaction 
from Welcome import Welcome
from Invites import Invites 
from Moderation import ModerationCog
from Ticket import TicketCog
# Define intents
intents = discord.Intents.all()
intents.message_content = True

# Initialize bot with intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Autoresponder dictionary to store messages for each channel
autoresponder_dict = {}
@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    bot.remove_command('help')
    await bot.tree.sync()
    economy_cog = Economy(bot)
    await bot.add_cog(economy_cog)
    await bot.add_cog(Leveling(bot))
    await bot.add_cog(GiveawayCog(bot))
    
    await bot.add_cog(SlashCommandCog(bot))
# Add Economy cog to bot
    await bot.add_cog(TicketCog(bot))
    await bot.add_cog(FunCog(bot))
    await bot.add_cog(CountingCog(bot))
    await bot.add_cog(Welcome(bot))
    await bot.add_cog(Invites(bot))
    await bot.add_cog(ModerationCog(bot))
    await bot.add_cog(HelpCog(bot))
    await bot.add_cog(PokemonCog(bot))
print("loaded")
# Event: Command error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use !help to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing required argument. Please check the command usage.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("I don't have permission to perform that command.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to perform that command.")
    else:
        await ctx.send(f"An error occurred: {error}")

# Command: Ping
@bot.tree.command()
async def ping(interaction=discord.Interaction):
    await interaction.response.send_message("Pong!")

#lovecal
# Command: Love Calculator
@bot.command(name='lovecal', help='Calculate the love percentage between two users')
async def love_calculator(ctx, user1: str, user2: str):
    # Extract names from user input
    name1 = user1
    name2 = user2

    # Generate a random love percentage
    love_percentage = random.randint(0, 100)

    # Format the result message
    result_message = f"Calculating love percentage between {name1} and {name2}..."

    # Send the initial message
    calculation_message = await ctx.send(result_message)

    # Simulate calculation delay
    await asyncio.sleep(2)

    # Update message with the result
    result_message = f"Love percentage between {name1} and {name2}: {love_percentage}% ❤️"
    await calculation_message.edit(content=result_message)



# Add more commands and event handlers here if needed


# Command: Calculator
@bot.command(name='calculator', aliases=['cal'])
async def calculator(ctx, *, expression: str):
    try:
        # Implementation of calculator
        await ctx.send("Calculation result...")
    except Exception as e:
        await ctx.send(f'Error in calculation: {e}')

# Command: DM User
@bot.command(name='dm')
async def dm_user(ctx, user_arg: str, *, message: str):
    try:
        # Implementation of DM user
        await ctx.send("Message sent successfully.")
    except discord.NotFound:
        await ctx.send(f'User not found. Unable to send a direct message.')
    except discord.Forbidden:
        await ctx.send(f'Unable to send a direct message to the user.')

# Command: Give Role
@bot.command()
async def giverole(ctx, role: discord.Role, member: discord.Member):
    await member.add_roles(role)
    await ctx.send(f'{member.mention} has been given the role: {role.name}')

# Command: Say
@bot.command()
async def say(ctx, *, message: str):
    await ctx.send(message)

# Command: Clear
@bot.command()
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)

# Command: Autoresponder
@bot.command(name="auto")
async def autoresponder(ctx, action: str, *args):
    if action.lower() == "add":
        try:
            trigger, response = args
            autoresponder_dict[trigger.lower()] = response
            save_autoresponder()
            await ctx.send(f"Autoresponder added for '{trigger}': '{response}'")
        except ValueError:
            await ctx.send("Invalid syntax. Use `!auto add (trigger) (response)`")
    elif action.lower() == "remove":
        try:
            trigger = args[0].lower()
            if trigger in autoresponder_dict:
                del autoresponder_dict[trigger]
                save_autoresponder()
                await ctx.send(f"Autoresponder removed for '{trigger}'")
            else:
                await ctx.send("No autoresponder found for the specified trigger.")
        except IndexError:
            await ctx.send("Invalid syntax. Use `!auto remove (trigger)`")
    else:
        await ctx.send("Invalid action. Use `!auto add (trigger) (response)` or `!auto remove (trigger)`")

# Event: Message event for custom autoresponder
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content_lower = message.content.lower()

    if content_lower in autoresponder_dict:
        await message.channel.send(autoresponder_dict[content_lower])

    await bot.process_commands(message)

# Command: Poll
@bot.command(name='poll')
async def poll(ctx, question: str, *options):
    total_options = len(options)

    if total_options > 8:
        await ctx.send("Sorry, the maximum number of options for a poll is 8.")
        return

    poll_message = await ctx.send(f'Poll: {question}\n')

    for option in options:
        await poll_message.add_reaction('👍')  # Thumbs up emoji as a voting option

    await poll_message.add_reaction('❌')  # Option to close the poll

# Event: Reaction Added for poll
@bot.event
async def on_reaction_add(reaction, user):
    # Check if the reaction is on a poll message
    if reaction.message.content.startswith('Poll:'):
        total_votes = sum([reaction.count for reaction in reaction.message.reactions]) - 1  # Exclude the bot's reaction

        if total_votes > 0:
            percentages = [(reaction.emoji, (reaction.count - 1) / total_votes * 100, reaction.count - 1) for reaction in reaction.message.reactions]
            percentages.sort(key=lambda x: x[1], reverse=True)

            percentage_text = '\n'.join([f'{emoji} : {percentage:.2f}% ({count} votes)' for emoji, percentage, count in percentages])

            await reaction.message.edit(content=f'{reaction.message.content}\n\nPoll Results:\n{percentage_text}')

# Dictionary to store user balances
user_balances = {}
# ... (Previous code)

# Command: Rock, Paper, Scissors (rps)
@bot.command(name='rps')
async def rock_paper_scissors(ctx: Context):
    choices = ['🪨', '📄', '✂️']

    message = await ctx.send("Choose your move: Rock, Paper, or Scissors?")
    for emoji in choices:
        await message.add_reaction(emoji)

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in choices

    try:
        reaction, _ = await bot.wait_for('reaction_add', timeout=30.0, check=check)
        user_choice = choices.index(str(reaction.emoji))

        bot_choice = random.choice(choices)
        result = determine_winner(user_choice, choices.index(bot_choice))

        await ctx.send(f"You chose {choices[user_choice]}\nI choose chose {bot_choice}\nResult: {result}")
    except TimeoutError:
        await ctx.send("You took too long to make a choice.")

def determine_winner(user_choice, bot_choice):
    if user_choice == bot_choice:
        return "It's a tie!"
    elif (user_choice + 1) % 3 == bot_choice:
        return "You win!"
    else:
        return "Bot wins!"

  # ... (Previous code)
# ... (Previous code)

# Command: Blackjack
@bot.command(name='bj')
async def blackjack(ctx: commands.Context, action: str = None, amount: int = 0):
    if ctx.author.id not in user_balances:
        user_balances[ctx.author.id] = 1000

    if action == 'bet':
        if amount <= 0 or amount > user_balances[ctx.author.id]:
            await ctx.send("Invalid bet amount. 🚫")
            return

        # Deal initial cards
        user_hand = [draw_card(), draw_card()]
        bot_hand = [draw_card(), draw_card()]

        await ctx.send(f"You placed a bet of ${amount} in Blackjack. Your hand: {user_hand} ♠️ ♥️")

        # Add buttons for hit and stand
        message = await ctx.send("Do you want to hit or stand? (React with 👍 for Hit or 👎 for Stand) 🃏")
        await message.add_reaction('👍')  # Hit
        await message.add_reaction('👎')  # Stand

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['👍', '👎']

        try:
            reaction, _ = await bot.wait_for('reaction_add', timeout=30.0, check=check)
            while str(reaction.emoji) == '👍':
                user_hand.append(draw_card())
                await ctx.send(f"Your hand: {user_hand} ♠️")
                if calculate_hand_value(user_hand) > 21:
                    await ctx.send("Bust! You went over 21. Game over. 💥")
                    return
                message = await ctx.send("Do you want to hit or stand? (React with 👍 for Hit or 👎 for Stand) 🃏")
                await message.add_reaction('👍')  # Hit
                await message.add_reaction('👎')  # Stand
                reaction, _ = await bot.wait_for('reaction_add', timeout=30.0, check=check)
            else:
                # Bot's turn
                while calculate_hand_value(bot_hand) < 17:
                    bot_hand.append(draw_card())

                await ctx.send(f"Bot's hand: {bot_hand} ♠️")

                # Determine the winner
                user_value = calculate_hand_value(user_hand)
                bot_value = calculate_hand_value(bot_hand)

                if user_value > 21:
                    result = "Bust! You went over 21. You lose. 💔"
                elif bot_value > 21 or user_value > bot_value:
                    result = f"You win! Your hand ({user_value}) beats the bot's hand ({bot_value}). 🎉"
                    user_balances[ctx.author.id] += amount * 2  # Double the bet for winning
                elif user_value == bot_value:
                    result = "It's a tie! Your bet is returned. 🤝"
                    user_balances[ctx.author.id] += amount  # Return the bet for a tie
                else:
                    result = f"You lose! Your hand ({user_value}) is lower than the bot's hand ({bot_value}). 💔"

                await ctx.send(result)
        except TimeoutError:
            await ctx.send("You took too long to decide. The game is over. ⌛")
            return

    elif action == 'claim':
        # ... (Previous code)
        await ctx.send(f"Your current balance: ${user_balances[ctx.author.id]} 💸")
    else:
        await ctx.send("Invalid action. Use `!bj bet (amount)`, `!bj claim`, or `!bj balance`. ❌")

# Function to draw a random card
def draw_card():
    cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    return random.choice(cards)

# Function to calculate the value of a hand
def calculate_hand_value(hand):
    values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}
    value = sum([values[card] for card in hand])

    # Adjust the value if there are aces
    num_aces = hand.count('A')
    while value > 21 and num_aces:
        value -= 10
        num_aces -= 1

    return value
  # Fortune Teller
@bot.command(name='fortune')
async def fortune(ctx):
    fortunes = [
        "A journey of a thousand miles begins with a single step.",
        "Don't count your chickens before they hatch.",
        "The early bird catches the worm.",
        "All that glitters is not gold.",
        "You will have a pleasant surprise.",
    ]
    random_fortune = random.choice(fortunes)
    await ctx.send(f'Your fortune: {random_fortune}')

# Trivia Quiz
@bot.command(name='quiz')
async def trivia_quiz(ctx):
    questions = [
        {"question": "What is the capital of France?", "options": ["Paris", "Berlin", "Madrid"], "correct": "Paris"},
        {"question": "Which planet is known as the Red Planet?", "options": ["Mars", "Venus", "Jupiter"], "correct": "Mars"},
        {"question": "Who wrote 'Romeo and Juliet'?", "options": ["Charles Dickens", "William Shakespeare", "Jane Austen"], "correct": "William Shakespeare"},
    ]

    question = random.choice(questions)
    options = '\n'.join([f'{index + 1}. {option}' for index, option in enumerate(question["options"])])

    await ctx.send(f'Question: {question["question"]}\nOptions:\n{options}')

    def check(message):
        return message.author == ctx.author and message.content.isdigit() and 1 <= int(message.content) <= len(question["options"])

    try:
        response = await bot.wait_for('message', timeout=30.0, check=check)
        selected_option = question["options"][int(response.content) - 1]

        if selected_option == question["correct"]:
            await ctx.send("Correct! 🎉")
        else:
            await ctx.send(f"Wrong! The correct answer was {question['correct']}. 💔")
    except TimeoutError:
        await ctx.send("You took too long to answer. The quiz is over. ⌛")
# Function to get a random activity suggestion from the Bored API
def get_random_activity():
    url = "https://www.boredapi.com/api/activity"
    response = requests.get(url)
    data = response.json()
    return data["activity"]

# Function to get a random fortune from the Fortune API
def get_random_fortune():
    url = "https://api.kanye.rest/"
    response = requests.get(url)
    data = response.json()
    return data["quote"]
# Remember Command
@bot.command(name='remember')
async def remember(ctx, *, info):
    # Store the information in a dictionary with the user's ID as the key
    user_id = ctx.author.id
    # Check if the user already has information stored
    if user_id in user_info:
        await ctx.send("You already have information stored. Use `!recall` to see it.")
    else:
        user_info[user_id] = info
        await ctx.send("Information stored successfully.")

# Recall Command
@bot.command(name='recall')
async def recall(ctx):
    user_id = ctx.author.id
    if user_id in user_info:
        info = user_info[user_id]
        await ctx.send(f"Here is the information you stored: {info}")
    else:
        await ctx.send("You don't have any information stored. Use `!remember` to store some.")

# User Info Command
@bot.command(name='userinfo')
async def user_info(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title="User Information", color=member.color)
    embed.set_thumbnail(url=member.avatar_url)
    embed.add_field(name="Name", value=member.display_name)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    embed.add_field(name="Join Date", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"))
    await ctx.send(embed=embed)

# Lock Command
@bot.command(name='lock')
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("Channel locked.")

# Ban Command
@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"{member.mention} has been banned.")

# Fun Commands
@bot.command(name='compliment')
async def compliment(ctx):
    compliments = [
        "You're amazing!",
        "You're a star!",
        "You're doing great!",
        "You're one of a kind!",
        "You're fantastic!",
    ]
    random_compliment = random.choice(compliments)
    await ctx.send(random_compliment)

@bot.command(name='insult')
async def insult(ctx):
    insults = [
        "You're a potato!",
        "You must be a magician because whenever I look at you, everyone else disappears!",
        "You're so slow, snails leave a trail to pass you!",
        "You're not stupid; you just have bad luck thinking!",
    ]
    random_insult = random.choice(insults)
    await ctx.send(random_insult)

@bot.command()
async def create_channel(ctx, channel_name: str):
    """Create a new text channel."""
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)

    if existing_channel:
        await ctx.send(f"Channel '{channel_name}' already exists!")
    else:
        try:
            new_channel = await guild.create_text_channel(channel_name)
            await ctx.send(f"Channel '{channel_name}' has been created successfully!")
        except discord.Forbidden:
            await ctx.send("You don't have permission to create channels in this server.")   
@bot.command()
async def create_category(ctx, category_name: str, role: discord.Role):
    """Create a new category with specific role permissions."""
    guild = ctx.guild
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),  # Restrict access for @everyone
        role: discord.PermissionOverwrite(read_messages=True)  # Allow access for the specified role
    }
    category = await guild.create_category(category_name, overwrites=overwrites)
    await ctx.send(f"Category '{category_name}' created with role permissions for {role.mention}.")
# Keep the bot running 24/7 with keep_alive
# Run the bot

TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
