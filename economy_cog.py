import discord
from discord.ext import commands
import sqlite3
import random

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('economy.db')  # Connect to the database
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS balances (
                              user_id TEXT PRIMARY KEY,
                              balance INTEGER DEFAULT 1000
                          )''')
        self.conn.commit()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS stocks (
                              company TEXT PRIMARY KEY,
                              price INTEGER
                          )''')
        self.conn.commit()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS portfolios (
                              user_id TEXT,
                              company TEXT,
                              quantity INTEGER,
                              PRIMARY KEY (user_id, company),
                              FOREIGN KEY (user_id) REFERENCES balances (user_id)
                          )''')
        self.conn.commit()

        # Initial stock prices for big companies
        self.stocks = {
            "Apple": 150,
            "Google": 250,
            "Amazon": 300,
            "Microsoft": 200,
            "Tesla": 400,
            "Facebook": 220,
            "Netflix": 280,
            "Intel": 180,
            "Nvidia": 350,
            "Disney": 260
        }
    @commands.command()
    async def buy_stock(self, ctx, company: str, quantity: int):
        """Buy stocks from a company."""
        company = company.capitalize()
        if company not in self.stocks:
            await ctx.send("Company not found.")
            return

        price = self.stocks[company]
        total_cost = price * quantity

        user_id = ctx.author.id
        current_balance = self.get_balance(user_id)

        if current_balance < total_cost:
            await ctx.send("You do not have enough funds to buy these stocks.")
            return

        # Update user balance and add stocks to their portfolio
        self.update_balance(user_id, -total_cost)
        self.add_to_portfolio(user_id, company, quantity)

        await ctx.send(f"You have successfully bought {quantity} shares of {company} for {total_cost} coins.")

    @commands.command()
    async def sell_stock(self, ctx, company: str, quantity: int):
        """Sell stocks from a company."""
        company = company.capitalize()
        if company not in self.stocks:
            await ctx.send("Company not found.")
            return

        current_price = self.stocks[company]
        total_gain = current_price * quantity

        user_id = ctx.author.id
        user_stocks = self.get_user_stocks(user_id)

        if company not in user_stocks or user_stocks[company] < quantity:
            await ctx.send("You do not have enough stocks to sell.")
            return

        # Calculate profit or loss
        purchase_price = self.get_purchase_price(company, quantity)
        profit_loss = total_gain - purchase_price

        # Update user balance and remove stocks from their portfolio
        self.update_balance(user_id, total_gain)
        self.remove_from_portfolio(user_id, company, quantity)

        await ctx.send(f"You have successfully sold {quantity} shares of {company} for {total_gain} coins. "
                       f"Profit/Loss: {profit_loss} coins.")

    @commands.command()
    async def report(self, ctx):
        """View report of sold stocks."""
        user_id = ctx.author.id
        sold_stocks = self.get_sold_stocks(user_id)

        if not sold_stocks:
            await ctx.send("You haven't sold any stocks yet.")
            return

        report_info = "\n".join([f"{company}: Bought: {bought}, Sold: {sold}, Profit/Loss: {profit}" 
                                 for company, (bought, sold, profit) in sold_stocks.items()])
        await ctx.send(f"Stocks Sold Report:\n{report_info}")
    @commands.command()
    async def buy_stock(self, ctx, company: str, quantity: int):
        """Buy stocks from a company."""
        company = company.capitalize()
        if company not in self.stocks:
            await ctx.send("Company not found.")
            return

        price = self.stocks[company]
        total_cost = price * quantity

        user_id = ctx.author.id
        current_balance = self.get_balance(user_id)

        if current_balance < total_cost:
            await ctx.send("You do not have enough funds to buy these stocks.")
            return

        # Update user balance and add stocks to their portfolio
        self.update_balance(user_id, -total_cost)
        self.add_to_portfolio(user_id, company, quantity)

        await ctx.send(f"You have successfully bought {quantity} shares of {company} for {total_cost} coins.")

    @commands.command()
    async def sell_stock(self, ctx, company: str, quantity: int):
        """Sell stocks from a company."""
        company = company.capitalize()
        if company not in self.stocks:
            await ctx.send("Company not found.")
            return

        current_price = self.stocks[company]
        total_gain = current_price * quantity

        user_id = ctx.author.id
        user_stocks = self.get_user_stocks(user_id)

        if company not in user_stocks or user_stocks[company] < quantity:
            await ctx.send("You do not have enough stocks to sell.")
            return

        # Calculate profit or loss
        purchase_price = self.get_purchase_price(company, quantity)
        profit_loss = total_gain - purchase_price

        # Update user balance and remove stocks from their portfolio
        self.update_balance(user_id, total_gain)
        self.remove_from_portfolio(user_id, company, quantity)

        await ctx.send(f"You have successfully sold {quantity} shares of {company} for {total_gain} coins. "
                       f"Profit/Loss: {profit_loss} coins.")

    @commands.command()
    async def report(self, ctx):
        """View report of sold stocks."""
        user_id = ctx.author.id
        sold_stocks = self.get_sold_stocks(user_id)

        if not sold_stocks:
            await ctx.send("You haven't sold any stocks yet.")
            return

        report_info = "\n".join([f"{company}: Bought: {bought}, Sold: {sold}, Profit/Loss: {profit}" 
                                 for company, (bought, sold, profit) in sold_stocks.items()])
        await ctx.send(f"Stocks Sold Report:\n{report_info}")

    @commands.command(aliases=['ehelp'])
    async def ecohelp(self, ctx):
        """Displays help and instructions for the economy system."""
        # Introduction and Instructions
        intro = (
            "Welcome to the Economy System!\n"
            "Earn coins through various activities and manage your finances!\n\n"
            "**Instructions:**\n"
            "- Use `!bal` to check your current balance.\n"
            "- Use `!deposit [amount]` to deposit coins into your account.\n"
            "- Use `!withdraw [amount]` to withdraw coins from your account.\n"
            "- Use `!loan [amount]` to take a loan.\n"
            "- Use `!pay [user] [amount]` to pay another user.\n"
            "- Use `!bet [amount]` to bet coins on a game.\n"
            "- Use `!daily_reward` to claim your daily reward.\n"
            "- Use `!give [user] [amount]` to give coins to another user (admin only).\n"
            "- Use `!take [user] [amount]` to take coins from another user (admin only).\n"
            "- Use `!reset [user]` to reset a user's balance to 0 (admin only).\n"
            "- Use `!leaderboard` to view the top 10 users with the highest balances.\n"
            "- Use `!transfer [user] [amount]` to transfer coins to another user.\n"
            "- Use `!buy [item]` to buy an item from the shop.\n"
            "- Use `!sell [item]` to sell an item to the shop.\n"
            "- Use `!invest [amount]` to invest coins in the stock market.\n"
            "- Use `!blackmarket [item]` to buy or sell illegal items on the black market.\n"
            "- Use `!buy_stock [company] [quantity]` to buy stocks from a company.\n"
            "- Use `!sell_stock [company] [quantity]` to sell stocks from a company.\n"
            "- Use `!stock_price [company]` to check the current price of a stock.\n"
            "- Use `!portfolio` to view your stock portfolio.\n"
            "- Use `!report` to view a report of your sold stocks.\n"
            "- Use `!invest [amount]` to invest coins in the stock market.\n"
            "- Use `!blackmarket [item]` to buy or sell illegal items on the black market.\n"
        )

        # Sending the help message with an embedded format
        embed = discord.Embed(title="Economy System Help", description=intro, color=0x42f4f4)
        await ctx.send(embed=embed)

    # Helper methods for database operations...
    # Existing methods here...
    @commands.command()
    async def stock_price(self, ctx, company: str):
        """Check the current price of a stock."""
        company = company.capitalize()
        if company not in self.stocks:
            await ctx.send("Company not found.")
            return

        price = self.stocks[company]
        await ctx.send(f"The current price of {company} stock is {price} coins.")

    @commands.command()
    async def portfolio(self, ctx):
        """View your stock portfolio."""
        user_id = ctx.author.id
        user_stocks = self.get_user_stocks(user_id)

        if not user_stocks:
            await ctx.send("Your portfolio is empty.")
            return

        portfolio_info = "\n".join([f"{company}: {quantity} shares" for company, quantity in user_stocks.items()])
        await ctx.send(f"Your stock portfolio:\n{portfolio_info}")
    @commands.command()
    async def invest(self, ctx, amount: int):
        """Invest coins in the stock market."""
        if amount <= 0:
            await ctx.send("You cannot invest a non-positive amount.")
            return

        user_id = ctx.author.id
        current_balance = self.get_balance(user_id)

        if current_balance < amount:
            await ctx.send("You do not have enough coins to invest this amount.")
            return

        # Implement your investment logic here
        # For example, you can randomly determine the outcome of the investment

        # For demonstration purposes, let's assume a 50% chance of success
        success = random.choice([True, False])

        if success:
            self.update_balance(user_id, amount)
            await ctx.send(f"You have successfully invested {amount} coins and earned a profit!")
        else:
            self.update_balance(user_id, -amount)
            await ctx.send(f"Unfortunately, your investment of {amount} coins did not yield any profit.")

    @commands.command()
    async def blackmarket(self, ctx, item: str):
        """Buy or sell illegal items on the black market."""
        # Implement your black market logic here
        # This can include buying or selling illegal items with risks and rewards

        # For demonstration purposes, let's just simulate a random outcome
        outcome = random.choice(["You successfully acquired the item!", "Your attempt to acquire the item failed!"])
        await ctx.send(outcome)

    # Add more commands here, if needed
