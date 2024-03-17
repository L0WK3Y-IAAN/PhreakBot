import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


# Load the HashCog cog
async def load():
    for root, _, files in os.walk('./cogs'):
        for filename in files:
            if filename.endswith('.py'):
                # Construct the module name
                module_name = f"cogs.{os.path.relpath(os.path.join(root, filename), 'cogs')[:-3].replace(os.sep, '.')}"
                # Load the extension
                await bot.load_extension(module_name)


async def main():
    await load()
    await bot.start(TOKEN)


asyncio.run(main())
