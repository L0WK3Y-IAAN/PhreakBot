import os
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv


# Load the bot token from the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Ensure your bot has message content intent enabled
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def get_last_10_messages(ctx):
    # Replace '1206818945030426625' with the channel ID you want to fetch messages from
    channel = bot.get_channel(1206818945030426625)
    
    # Fetch the last 10 messages from the channel
    async for message in channel.history(limit=10):
        print(f"Message content: {message.content}")
        print(f"Author: {message.author}")
        print(f"Timestamp: {message.created_at}")
        
        # Check if the message is a reply
        if message.reference:
            referenced_message = await channel.fetch_message(message.reference.message_id)
            print(f"Replied to: {referenced_message.author}: {referenced_message.content}")
        
        print("--------------------")

bot.run(TOKEN)
