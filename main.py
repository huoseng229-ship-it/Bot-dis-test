import discord
from discord.ext import commands
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')

@bot.event
async def on_message(message):
    # Don't respond to the bot's own messages
    if message.author == bot.user:
        return
    
    # Process commands
    await bot.process_commands(message)

@bot.command(name='hello')
async def hello(ctx):
    """Say hello to the user"""
    await ctx.send(f'Hello {ctx.author.mention}! 👋')

@bot.command(name='ping')
async def ping(ctx):
    """Check bot latency"""
    latency = round(bot.latency * 1000)
    await ctx.send(f'Pong! Latency: {latency}ms')

@bot.command(name='info')
async def info(ctx):
    """Display bot information"""
    embed = discord.Embed(
        title="Bot Information",
        description="A simple Discord bot created with discord.py",
        color=0x00ff00
    )
    embed.add_field(name="Guilds", value=len(bot.guilds), inline=True)
    embed.add_field(name="Users", value=len(bot.users), inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    await ctx.send(embed=embed)

@bot.command(name='say')
async def say(ctx, *, message):
    """Make the bot say something"""
    await ctx.send(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found! Use `!help` to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing required argument! Check the command usage with `!help <command>`")
    else:
        print(f"Error: {error}")
        await ctx.send("An error occurred while processing the command.")

# Run the bot
if __name__ == "__main__":
    # Get bot token from environment variable
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("ERROR: DISCORD_BOT_TOKEN environment variable not found!")
        print("Please set your Discord bot token using the secrets manager.")
        exit(1)
    
    # Debug info (without revealing the actual token)
    print(f"Token found - Length: {len(token)} characters")
    if len(token) < 50:
        print("WARNING: Token seems too short. Discord bot tokens are typically 70+ characters.")
        print("Make sure you copied the full token from the Discord Developer Portal.")
    
    try:
        bot.run(token)
    except discord.LoginFailure:
        print("ERROR: Invalid bot token!")
    except Exception as e:
        print(f"ERROR: {e}")