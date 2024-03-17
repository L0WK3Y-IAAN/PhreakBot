import os
import asyncio  # Import asyncio for the sleep function
import discord
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone


# Load the bot token from the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Ensure your bot has message content intent enabled
client = discord.Client(intents=intents)

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Dictionary to store the last bump time for each channel
last_bump_time = {}

async def send_bump_reminder(channel_id):
    """Sends a bump reminder after 2 hours since the last bump."""
    await asyncio.sleep(2 * 60 * 60)  # Wait for 2 hours
    current_time = datetime.utcnow()

    if channel_id in last_bump_time:
        time_since_last_bump = current_time - last_bump_time[channel_id]
        if time_since_last_bump >= timedelta(hours=2):
            await client.get_channel(channel_id).send("@here You can bump now!")



@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    logging.info("Bot is ready and logged in as %s", client.user)

async def find_last_bump_message(channel):
    async for message in channel.history(limit=100):
        if message.author.bot and message.embeds:
            if "Bump done!" in message.embeds[0].description:
                return message.created_at.replace(tzinfo=timezone.utc)  # Make it offset-aware
    return None

@client.event
async def on_message(message):
    current_time = datetime.now(timezone.utc)  # Make it offset-aware

    if message.content.startswith('/bump') and not message.author.bot and message.channel.id == 1206818945030426625:
        # Log and print the user who used the bump command and the timestamp
        user_info = f'User {message.author} (ID: {message.author.id}) used /bump in channel {message.channel.name} at {current_time.strftime("%Y-%m-%d %H:%M:%S")} UTC\n'
        await message.channel.send(f'You can bump again in 2 hours.')
        print(user_info)  # user_info is defined in this block, so it's safe to use
        last_bump_time[message.channel.id] = current_time
        asyncio.create_task(send_bump_reminder(message.channel.id))

    elif message.content.startswith('!check_bump') or message.content.startswith('!cb') and message.channel.id == 1206818945030426625:
        channel_id = message.channel.id

        last_bump_time[channel_id] = await find_last_bump_message(message.channel)
        if last_bump_time[channel_id] is None:
            await message.channel.send("No recent bump message found.")
            return

        time_since_last_bump = current_time - last_bump_time[channel_id]
        remaining_time = timedelta(hours=2) - time_since_last_bump

        if remaining_time.total_seconds() > 0:
            hours, remainder = divmod(int(remaining_time.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            await message.channel.send(f'You can bump again in {hours}h {minutes}m {seconds}s.')
        else:
            await message.channel.send("@here You can bump now!")

client.run(TOKEN)

