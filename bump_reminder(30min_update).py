import os
import asyncio
import discord
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

# Load the bot token from the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Dictionary to store the last bump time for each channel
last_bump_time = {}

async def bump_timer(channel_id):
    """Handles the bump timing, reminders, and updates."""
    bump_interval = timedelta(hours=2)  # 2 hours
    update_interval = timedelta(minutes=30)  # 30 minutes
    next_update_time = datetime.now(timezone.utc) + update_interval

    while channel_id in last_bump_time:
        current_time = datetime.now(timezone.utc)
        time_since_last_bump = current_time - last_bump_time[channel_id]
        remaining_time = bump_interval - time_since_last_bump

        if remaining_time <= timedelta(0):
            try:
                await client.get_channel(channel_id).send("@here You can bump now!")
                return  # End the loop after sending the bump reminder
            except Exception as e:
                logging.error(f"Error sending bump reminder: {e}")
                return  # End the loop if there's an error sending the message

        # Check if it's time for the next update
        if current_time >= next_update_time:
            hours, remainder = divmod(int(remaining_time.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            try:
                await client.get_channel(channel_id).send(f"You can bump again in {hours}h {minutes}m.")
                next_update_time += update_interval  # Set the time for the next update
            except Exception as e:
                logging.error(f"Error sending update message: {e}")
                # Continue the loop even if there's an error

        await asyncio.sleep(10)  # Check more frequently to reduce the chance of missing the update window



@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    logging.info("Bot is ready and logged in as %s", client.user)
    specific_channel_id = 123456789012345678  # Replace this with the actual channel ID
    asyncio.create_task(bump_timer(specific_channel_id))


@client.event
async def on_message(message):
    if message.content.startswith('bump') and not message.author.bot and message.channel.id == 1206818945030426625:
        current_time = datetime.now(timezone.utc)
        user_info = f'User {message.author} (ID: {message.author.id}) used /bump in channel {message.channel.name} at {current_time.strftime("%Y-%m-%d %H:%M:%S")} UTC\n'
        print(user_info)
        await message.channel.send('You can bump again in 2 hours.')
        last_bump_time[message.channel.id] = current_time
        asyncio.create_task(bump_timer(message.channel.id))


client.run(TOKEN)
