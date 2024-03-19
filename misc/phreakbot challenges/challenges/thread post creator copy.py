'''
🔴 - Add a number of CTF's created, which CTF's they created, and which CTF's they solved to leaderboard
🔴 - Fix leaderboard so that it post the ctf creator data
🔴 - Password protect the zip file
'''


import os
from time import sleep
import discord
import json
import asyncio
from dotenv import load_dotenv

# Load the bot token from the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.guilds = True
intents.members = True  # This line is necessary to access the member list
client = discord.Client(intents=intents)

set_thread_name = "Not This Again..."
set_difficulty = "🔴 Hard"
set_points_reward = "✨ 200"
SET_FLAG = os.getenv('NOT_THIS_AGAIN_FLAG')

# Get the directory of the running script
script_dir = os.path.dirname(os.path.realpath(__file__))
json_path = os.path.join(script_dir, 'threads.json')

async def post_thread(forum_channel, thread_name, embed, file_path=None):
    # Get the current threads in the forum channel
    current_threads = forum_channel.threads
    current_thread_names = {thread.name for thread in current_threads}

    # Check if the thread already exists in the forum channel
    if thread_name in current_thread_names:
        print(f"Thread '{thread_name}' already exists in the forum channel.")
        return None  # Return None to indicate that no new thread was created

    # Post the thread to Discord
    files = [discord.File(file_path)] if file_path else []
    thread_with_message = await forum_channel.create_thread(name=thread_name, content="", embed=embed, files=files)
    new_thread = thread_with_message.thread  # Access the thread from the ThreadWithMessage object
    print(f"New thread created: {new_thread} (Type: {type(new_thread)})")

    # Update the JSON file with the new thread's ID
    new_thread_data = {
        'id': new_thread.id,
        'name': thread_name,
        'embed': embed.to_dict(),
        'file_path': file_path
    }
    with open(json_path, 'r') as f:
        existing_thread_data = json.load(f)
    existing_thread_data.append(new_thread_data)
    with open(json_path, 'w') as f:
        json.dump(existing_thread_data, f)
    
    # Update the global variable with the new thread's ID
    global current_forum_thread_id
    current_forum_thread_id = new_thread.id

    return new_thread  # Return the new_thread object



async def update_threads_json(forum_channel):
    
    await build_thread_mapping()  # Rebuild the mapping after updating the JSON file

    # Get the current threads in the forum channel
    current_threads = forum_channel.threads
    current_thread_ids = {thread.id for thread in current_threads}

    # Check if the JSON file exists, if not, create it
    if not os.path.exists(json_path):
        with open(json_path, 'w') as f:
            json.dump([], f)

    # Load the existing thread data from the JSON file
    try:
        with open(json_path, 'r') as f:
            existing_thread_data = json.load(f)
    except json.JSONDecodeError:
        existing_thread_data = []

    # Filter out threads that no longer exist on Discord
    updated_thread_data = [thread for thread in existing_thread_data if thread['id'] in current_thread_ids]

    # Write the updated thread data to the JSON file
    with open(json_path, 'w') as f:
        json.dump(updated_thread_data, f)



async def create_thread_if_not_exists(forum_channel, thread_name, starting_message, file_path):
    threads = forum_channel.threads
    if not any(thread.name == thread_name for thread in threads):
        file = discord.File(file_path)
        await forum_channel.create_thread(name=thread_name, content=starting_message, files=[file])
        await update_threads_json(forum_channel)

forum_channel_id = 1216949753808421016  # Replace with your forum channel ID
current_forum_thread_id = None

async def check_and_repost_threads():
    # Specify the forum channel ID
    
    # Find the forum channel
    forum_channel = client.get_channel(forum_channel_id)
    
    if forum_channel:
        await update_threads_json(forum_channel)
        # Load existing thread data from JSON
        with open(json_path, 'r') as f:
            existing_thread_data = json.load(f)
        
        # Get the names of the current threads in the forum channel
        current_thread_names = {thread.name for thread in forum_channel.threads}

        # Check for threads in the JSON that don't exist on Discord and repost them
        for thread_data in existing_thread_data:
            # Check if a thread with the same name already exists in the forum channel
            if thread_data['name'] not in current_thread_names:
                file_path = thread_data['file_path']
                file = discord.File(file_path) if file_path else None
                await forum_channel.create_thread(name=thread_data['name'], content=thread_data['embed']['description'], embed=discord.Embed.from_dict(thread_data['embed']), files=[file])
    
    else:
        print(f'Forum channel with ID {forum_channel_id} not found')

# Global variable to track if the first correct submission has occurred
first_correct_submission = False

# Path to the leaderboard JSON file
leaderboard_path = os.path.join(script_dir, 'leaderboard.json')

def update_leaderboard(user_id, points, thread_name, first_blood=False):
    # Load the existing leaderboard data
    with open(leaderboard_path, 'r') as f:
        leaderboard = json.load(f)

    # Initialize the user's entry if not present
    user_data = leaderboard.setdefault(user_id, {'points': 0, 'solved': []})

    # Add points if the challenge hasn't been solved yet and the thread is new
    if thread_name not in user_data['solved']:
        user_data['points'] += points
        user_data['solved'].append(thread_name)
        if first_blood:
            user_data['points'] += 50  # First blood bonus

    # Save the updated leaderboard data
    with open(leaderboard_path, 'w') as f:
        json.dump(leaderboard, f, indent=4)

    return thread_name in user_data['solved']

# Specify the user ID
ctf_creator = 404141696322895872  # Replace with the user ID

@client.event
async def on_message(message):
    correct_flag = SET_FLAG

    # Use the global thread name to get the correct thread ID
    global set_thread_name
    thread_id = thread_name_to_id.get(set_thread_name)
    
    if not thread_id:
        print("Thread not found in mapping")
        return


    global first_correct_submission
    # global current_forum_thread_id

    # Check if the message is in the newly created forum thread and not from the bot itself
    # Now proceed only if there's a thread ID and the message is in that thread
    if message.channel.id == thread_id and message.author != client.user:

        # Prevent the ctf_creator from solving their own challenge
        if message.author.id == ctf_creator:
            await message.channel.send("Challenge creators can not solve their own challenges... Nice try though. 😉", delete_after=10)
            await message.delete()  # Optionally delete the creator's message
            return

        # Check if the bot is mentioned in the message
        if client.user.mentioned_in(message):
            # Strip the mention to get the flag text
            message_content = message.content.replace(f'<@!{client.user.id}>', '').replace(f'<@{client.user.id}>', '').strip()

            # Prevent the user from solving the challenge more than once
            user_id_str = str(message.author.id)
            with open(leaderboard_path, 'r') as f:
                leaderboard = json.load(f)
            if leaderboard.get(user_id_str, {}).get('solved', False):
                response = "You have already solved this challenge. 🎓"
                await message.channel.send(response, delete_after=5)
            else:
                # Check if the message content after removing the mention is the correct flag
                if message_content == correct_flag:
                    response = "Correct! 🥳"
                    points = 200  # Base points for a correct answer
                    thread_name = "THREAD_NAME_HERE"  # You need to determine the actual thread name

                    # Check if this is the first correct submission
                    if not first_correct_submission:
                        first_correct_submission = True
                        solved = update_leaderboard(user_id_str, points, set_thread_name, first_blood=True)
                        await message.delete()

                    else:
                        solved = update_leaderboard(user_id_str, points, thread_name)
                        await message.delete()

                    if solved:
                        await message.channel.send(response, delete_after=5)
                else:
                    response = "Incorrect. ❌"
                    await message.delete()
                    await message.channel.send(response, delete_after=5)
        else:
            # If the bot is not mentioned, delete the message and send a reminder
            await message.delete()
            reminder = "Be sure to ping the bot first in order to submit the flag."
            await message.channel.send(reminder, delete_after=10)

        # Print the message content to the terminal for debugging purposes
        print(f"Message from {message.author}: {message.content}")


async def background_task():
    while True:
        await check_and_repost_threads()
        await asyncio.sleep(60)  # Check every 60 seconds


def award_creator_points_once(creator_id, points, thread_name):
    with open(leaderboard_path, 'r+') as f:
        leaderboard = json.load(f)

        # Check if the creator has already been awarded points for this thread
        if creator_id not in leaderboard or thread_name not in leaderboard[creator_id]['solved']:
            update_leaderboard(creator_id, points, thread_name)  # Pass thread_name to the update function

            # Save the updated leaderboard data
            f.seek(0)  # Resets file position to the start
            json.dump(leaderboard, f, indent=4)
            f.truncate()  # Removes leftover data

thread_name_to_id = {}

async def build_thread_mapping():
    with open(json_path, 'r') as f:
        threads_data = json.load(f)
    global thread_name_to_id
    thread_name_to_id = {thread['name']: thread['id'] for thread in threads_data}

@client.event
async def on_ready():
    
    await build_thread_mapping()

    print(f'We have logged in as {client.user}')
    
    # Specify the forum channel ID
    forum_channel_id = 1216949753808421016  # Replace with your forum channel ID

    # Specify the guild (server) ID
    guild_id = 1174628900001824779  # Replace with your guild ID
    
    # Find the forum channel
    forum_channel = client.get_channel(forum_channel_id)

    # Find the guild
    guild = client.get_guild(guild_id)


    if forum_channel and guild:
        # Try to fetch the member (CTF creator) from the guild
        try:
            member = await guild.fetch_member(ctf_creator)
            if member:
                # Award points to the creator only once, use "Author Name" as the thread name
                award_creator_points_once(str(ctf_creator), 20, set_thread_name)
            embed = discord.Embed(title="Download", description="```I recieved some work docs from a co-worker and... Oh God... Not this again!\nPassword: infected```", url="https://github.com/L0WK3Y-IAAN/CTF-FIles/raw/main/unknown.zip")
            embed.set_author(name=set_thread_name)
            embed.add_field(name="Difficulty", value=f"```{set_difficulty}```", inline=True)
            embed.add_field(name="Completion Reward", value=f"```{set_points_reward}```", inline=True)
            embed.set_image(url="https://i.imgur.com/RwJiPsy.gif")
            embed.set_footer(text=member.display_name, icon_url=member.display_avatar.url if member.avatar else member.default_avatar.url)
            try:
                # Add a comma along with file path that you would like to upload
                await post_thread(forum_channel, embed.author.name, embed)
            except Exception as e:
                print(f"An error occurred: {e}")
            else:
                print(f'Member with ID {ctf_creator} not found in guild {guild_id}')
        except discord.NotFound:
            print(f'Member with ID {ctf_creator} not found in guild {guild_id}')
        except discord.HTTPException as e:
            print(f'HTTP error occurred: {e}')
    else:
        print(f'Forum channel with ID {forum_channel_id} not found or guild with ID {guild_id} not found')


# Use the loaded token to run the client
client.run(TOKEN)

