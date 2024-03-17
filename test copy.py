# This is new in the discord.py 2.0 update

# imports
import os
import discord
import discord.ext
from typing import Final
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands

# Load token from env
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# setting up the bot
# if you don't want all intents you can do discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

# sync the slash command to your server
@bot.event
async def on_ready():
    print("ready")
    try:
        synced = await bot.tree.sync()
        print (f"Synced {len(synced)} commmand(s)")
        # print "ready" in the console when the bot is ready to work
    except Exception as e:
        print(e)

# Hello slash command
@bot.tree.command(name='hello')
async def hello(ctx: discord.Interaction):
    await ctx.response.send_message(f"Hello {ctx.user.mention}")

# Say slash command
@bot.tree.command(name='say')
@app_commands.describe(thing_to_say="What should I say?")
async def say(ctx: discord.Interaction, thing_to_say: str):
    await ctx.response.send_message(f"{ctx.user.mention} said `{thing_to_say}`")

# Delete messages slash command
@bot.tree.command(name='deletemessages')
@app_commands.describe(amount="Number of messages to delete")
async def delete_messages(ctx : discord.Integration, amount: int):
    if ctx.user.guild_permissions.manage_messages:
        try:
            # Delete the specified number of messages
            deleted = await ctx.channel.purge(limit=amount)
            # Send a confirmation message
            await ctx.response.send_message(f"Deleted {len(deleted)} messages.", ephemeral=True)
        except discord.errors.NotFound:
            # Handle the case where the interaction is not found
            print("Interaction not found. Unable to send message.")
    else:
        # Send a message if the user doesn't have permissions
        await ctx.response.send_message("You don't have permission to use this command.", ephemeral=True)

# run the bot
bot.run(TOKEN)
