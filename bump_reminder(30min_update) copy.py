import os
import discord
import asyncio
from dotenv import load_dotenv
from discord.ext import commands, tasks

# Load the bot token from the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Initialize the bot with necessary intents
intents = discord.Intents.all()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    check_bump_reminder.start()

# Command to check the status of the bump
@bot.event
async def check_bump(ctx):
    # Define the channel ID where bump messages are sent
    channel_id = 1206818945030426625
    channel = bot.get_channel(channel_id)
    if not channel:
        await ctx.send("🔴 Channel not found!")
        return

    # Loop through the last 100 messages in the channel
    async for message in channel.history(limit=100):
        # Check if the message is an embed
        if isinstance(message, discord.Message) and message.embeds:
            # Loop through the embeds in the message
            for embed in message.embeds:
                # Check if the embed contains "Bump done!"
                if "Bump done!" in embed.description:
                    # Calculate the time since the bump
                    time_since_bump_seconds = (discord.utils.utcnow() - message.created_at).total_seconds()
                    hours = int(time_since_bump_seconds // 3600)
                    minutes = int((time_since_bump_seconds % 3600) // 60)
                    seconds = int(time_since_bump_seconds % 60)

                    if hours >= 2:
                        await ctx.send("@here You can bump again!")
                        print("\r🟢 Bump available!", end='', flush=True)
                    else:
                        time_left_seconds = round((2 * 3600) - time_since_bump_seconds)
                        remaining_hours = int(time_left_seconds // 3600)
                        remaining_minutes = int((time_left_seconds % 3600) // 60)
                        remaining_seconds = int(time_left_seconds % 60)

                        await ctx.send(f"You have to wait {remaining_hours} hours, {remaining_minutes} minutes, and {remaining_seconds} seconds before bumping again.")
                        print(f"Wait for {remaining_hours} hours, {remaining_minutes} minutes, and {remaining_seconds} seconds before bumping again.")
                    return
    await ctx.send("🔴 No recent bump found!")
    print("🔴 No recent bump found.")


# Background task to print remaining time to terminal every second
@tasks.loop(seconds=1)
async def check_bump_reminder():
    # Define the channel ID where bump messages are sent
    channel_id = 1206818945030426625
    channel = bot.get_channel(channel_id)
    if not channel:
        print("🔴 Channel not found!")
        return

    # Variable to store whether a bump was found
    bump_found = False

    # Loop through the last 100 messages in the channel
    async for message in channel.history(limit=100):
        # Check if the message is an embed
        if isinstance(message, discord.Message) and message.embeds:
            # Loop through the embeds in the message
            for embed in message.embeds:
                # Check if the embed contains a description
                if embed.description is not None:
                    # Check if the embed contains "Bump done!"
                    if "Bump done!" in embed.description:
                        # Calculate the time since the bump
                        time_since_bump_seconds = (discord.utils.utcnow() - message.created_at).total_seconds()
                        bump_found = True
                        if time_since_bump_seconds >= 2 * 3600:
                            print("\r🟢 Bump available!", end='', flush=True)
                        else:
                            time_left_seconds = round((2 * 3600) - time_since_bump_seconds)
                            remaining_hours = int(time_left_seconds // 3600)
                            remaining_minutes = int((time_left_seconds % 3600) // 60)
                            remaining_seconds = int(time_left_seconds % 60)

                            print(f"\r🔵 Remaining time: {remaining_hours} hours, {remaining_minutes} minutes, and {remaining_seconds} seconds before bumping again.", end='', flush=True)
    # If no recent bump was found, print the message
    if not bump_found:
        print("\r🔴 No recent bump found.", end='', flush=True)

check_bump_reminder.before_loop(bot.wait_until_ready)

# Run the bot
bot.run(TOKEN)
