import os
import discord
import json
from dotenv import load_dotenv
import asyncio
import time

# Load the bot token from the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Initialize Discord bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True  # Enable guild intents to access guild information
intents.members = True  # Enable member intents to access member information
bot = discord.Client(intents=intents)

# Leaderboard file path
leaderboard_file_path = '.\\misc\\phreakbot challenges\\challenges\\leaderboard.json'

# Store the initial modified time
file_last_modified = os.path.getmtime(leaderboard_file_path)

async def update_leaderboard_embed():
    global file_last_modified
    await bot.wait_until_ready()
    leaderboard_channel_id = 1217756961160822854  # The channel where you want to send the leaderboard

    while not bot.is_closed():
        try:
            # Check if the file has been modified
            current_modified_time = os.path.getmtime(leaderboard_file_path)
            if current_modified_time != file_last_modified:
                file_last_modified = current_modified_time

                # Load the leaderboard data from the JSON file
                with open(leaderboard_file_path, 'r') as f:
                    leaderboard = json.load(f)

                guild = bot.get_guild(1174628900001824779)  # Replace with your guild ID
                if guild is None:
                    print("Guild not found")
                    continue

                # Sort the leaderboard by points in descending order
                sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1]['points'], reverse=True)
                
                # Create the leaderboard embed
                leaderboard_embed = discord.Embed(title="Leaderboard", color=discord.Color.green())
                
                # Get the channel
                channel = bot.get_channel(leaderboard_channel_id)
                if channel is None:
                    print("Leaderboard channel not found")
                    continue

                # Add each user to the embed description
                leaderboard_embed.clear_fields()
                for index, (user_id, user_data) in enumerate(sorted_leaderboard, start=1):
                    member = await guild.fetch_member(int(user_id))
                    member_avatar_url = member.display_avatar.url if member.display_avatar else member.default_avatar.url
                    leaderboard_embed.add_field(name=f"{index}. {member.display_name}", value=f"{user_data['points']} points", inline=False)

                # Send the embed to the channel
                messages = [msg async for msg in channel.history(limit=10) if msg.author == bot.user and msg.embeds]
                if messages:
                    await messages[0].edit(embed=leaderboard_embed)
                else:
                    await channel.send(embed=leaderboard_embed)

        except Exception as e:
            print(f"An error occurred: {e}")

        await asyncio.sleep(10)  # Sleep for some time before checking again

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    bot.loop.create_task(update_leaderboard_embed())

# Run the bot
bot.run(TOKEN)
