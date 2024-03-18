# '''
# 🔴 - Add a number of CTF's created, which CTF's they created, and which CTF's they solved to leaderboard
# 🔴 - Fix leaderboard so that it post the ctf creator data
# 🔴 - Password protect the zip file
# '''


import os
from time import sleep
import discord
import json
import asyncio
from dotenv import load_dotenv
from discord.ext import commands

# Load the bot token from the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


set_thread_name = "Not This Again..."
set_difficulty = "🔴 Hard"
set_points_reward = "✨ 200"
SET_FLAG = os.getenv('NOT_THIS_AGAIN_FLAG')

class Not_This_Again_CTF(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.json_path = os.path.join(self.script_dir, 'threads.json')
        self.leaderboard_path = os.path.join(self.script_dir, 'leaderboard.json')
        self.forum_channel_id = 1216949753808421016  # Replace with your forum channel ID
        self.current_forum_thread_id = None
        self.first_correct_submission = False
        self.ctf_creator = 404141696322895872  # Replace with the user ID
        self.thread_name_to_id = {}


    @commands.Cog.listener()
    async def on_ready(self):
        await self.build_thread_mapping()
        print(f'We have logged in as {self.bot.user}')

        forum_channel = self.bot.get_channel(self.forum_channel_id)
        guild = self.bot.get_guild(1174628900001824779)  # Replace with your guild ID

        if forum_channel and guild:
            try:
                member = await guild.fetch_member(self.ctf_creator)
                if member:
                    embed = discord.Embed(
                        title="Download",
                        description="```A mysterious file arrived at the Security Operations Center (SOC), baffling the team with its cryptic contents. Unable to decipher its meaning, they escalated it to the Malware Analysis Team, where I was tasked with unraveling its secrets.\n\n🔒 Password: infected```",
                        url="https://github.com/L0WK3Y-IAAN/CTF-FIles/raw/main/unknown.zip"
                    )
                    embed.set_author(name=set_thread_name)
                    embed.add_field(name="Difficulty", value=f"```{set_difficulty}```", inline=True)
                    embed.add_field(name="Completion Reward", value=f"```{set_points_reward}```", inline=True)
                    embed.add_field(name="Flag Submission", value="```⚠️BE SURE TO @ THE BOT FOLLOWING YOUR FLAG SUBMISSION. Ex: @PhreakBot CTF{INSERT_FLAG_HERE}```", inline=True)
                    embed.set_image(url="https://i.imgur.com/RwJiPsy.gif")
                    embed.set_footer(text=member.display_name, icon_url=member.display_avatar.url if member.avatar else member.default_avatar.url)

                    new_thread = await self.post_thread(forum_channel, set_thread_name, embed)
                    if new_thread:
                        # Award points to the creator only once, after the thread is successfully created
                        await self.award_creator_points_once(str(self.ctf_creator), 20, set_thread_name)
            except discord.NotFound:
                print(f'Member with ID {self.ctf_creator} not found in guild {self.guild_id}')
            except discord.HTTPException as e:
                print(f'HTTP error occurred: {e}')
        else:
            print(f'Forum channel with ID {self.forum_channel_id} not found or guild not found')


    # Get the directory of the running script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    json_path = os.path.join(script_dir, 'threads.json')

    async def post_thread(self, forum_channel, thread_name, embed, file_path=None):
        # Get the current threads in the forum channel
        current_threads = forum_channel.threads
        current_thread_names = {thread.name for thread in current_threads}
        pass

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
        with open(self.json_path, 'r') as f:
            existing_thread_data = json.load(f)
        existing_thread_data.append(new_thread_data)
        with open(self.json_path, 'w') as f:
            json.dump(existing_thread_data, f)
        
        # Update the global variable with the new thread's ID
        global current_forum_thread_id
        current_forum_thread_id = new_thread.id

        return new_thread  # Return the new_thread object



    async def update_threads_json(self, forum_channel):
        
        await self.build_thread_mapping()  # Rebuild the mapping after updating the JSON file

        # Get the current threads in the forum channel
        current_threads = forum_channel.threads
        current_thread_ids = {thread.id for thread in current_threads}

        # Check if the JSON file exists, if not, create it
        if not os.path.exists(self.json_path):
            with open(self.json_path, 'w') as f:
                json.dump([], f)

        # Load the existing thread data from the JSON file
        try:
            with open(self.json_path, 'r') as f:
                existing_thread_data = json.load(f)
        except json.JSONDecodeError:
            existing_thread_data = []

        # Filter out threads that no longer exist on Discord
        updated_thread_data = [thread for thread in existing_thread_data if thread['id'] in current_thread_ids]

        # Write the updated thread data to the JSON file
        with open(self.json_path, 'w') as f:
            json.dump(updated_thread_data, f)
    pass



    async def create_thread_if_not_exists(self, forum_channel, thread_name, starting_message, file_path):
        threads = forum_channel.threads
        if not any(thread.name == thread_name for thread in threads):
            file = discord.File(file_path)
            await forum_channel.create_thread(name=thread_name, content=starting_message, files=[file])
            await self.update_threads_json(forum_channel)
    pass

    forum_channel_id = 1216949753808421016  # Replace with your forum channel ID
    current_forum_thread_id = None

    async def check_and_repost_threads(self):
        # Specify the forum channel ID
        
        # Find the forum channel
        forum_channel = self.bot.get_channel(self.forum_channel_id)
        
        if forum_channel:
            await self.update_threads_json(forum_channel)
            # Load existing thread data from JSON
            with open(self.json_path, 'r') as f:
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
            print(f'Forum channel with ID {self.forum_channel_id} not found')
    pass

    # Global variable to track if the first correct submission has occurred
    first_correct_submission = False

    # Path to the leaderboard JSON file
    leaderboard_path = os.path.join(script_dir, 'leaderboard.json')

    def update_leaderboard(self, user_id, points, thread_name, first_blood=False):
        # Load the existing leaderboard data
        with open(self.leaderboard_path, 'r') as f:
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
        with open(self.leaderboard_path, 'w') as f:
            json.dump(leaderboard, f, indent=4)

        return thread_name in user_data['solved']
    pass

    # Specify the user ID
    ctf_creator = 404141696322895872  # Replace with the user ID

    @commands.Cog.listener()
    async def on_message(self, message):
        correct_flag = SET_FLAG
        
        # Use the global thread name to get the correct thread ID
        global set_thread_name
        thread_id = self.thread_name_to_id.get(set_thread_name)
        
        print(f"Thread ID: {thread_id}, Message Channel ID: {message.channel.id}")
        
        if not thread_id:
            print("Thread not found in mapping")
            return

        if message.channel.id == thread_id and message.author != self.bot.user:
            if message.author.id == self.ctf_creator:
                await message.channel.send("Challenge creators cannot solve their own challenges.", delete_after=10)
                await message.delete()
                return

            if self.bot.user.mentioned_in(message):
                message_content = message.content.replace(f'<@!{self.bot.user.id}>', '').replace(f'<@{self.bot.user.id}>', '').strip()
                user_id_str = str(message.author.id)
                with open(self.leaderboard_path, 'r') as f:
                    leaderboard = json.load(f)
                
                if leaderboard.get(user_id_str, {}).get('solved', False):
                    response = "You have already solved this challenge."
                    await message.channel.send(response, delete_after=5)
                else:
                    if message_content == correct_flag:
                        response = "Correct! 🥳"
                        points = 200
                        thread_name = set_thread_name

                        if not self.first_correct_submission:
                            self.first_correct_submission = True
                            solved = self.update_leaderboard(user_id_str, points, thread_name, first_blood=True)
                            await message.channel.send("You got FIRST BLOOD!", delete_after=5)
                        else:
                            solved = self.update_leaderboard(user_id_str, points, thread_name)

                        if solved:
                            await message.channel.send(response, delete_after=5)
                        await message.delete()
                    else:
                        response = "Incorrect."
                        await message.channel.send(response, delete_after=5)
                        await message.delete()
            else:
                await message.delete()
                reminder = "Be sure to ping the bot first in order to submit the flag."
                await message.channel.send(reminder, delete_after=10)


            # Print the message content to the terminal for debugging purposes
            print(f"Message from {message.author}: {message.content}")


    async def background_task(self):
        while True:
            await self.check_and_repost_threads()
            await asyncio.sleep(60)  # Check every 60 seconds


    async def award_creator_points_once(self, creator_id, points, thread_name):
        with open(self.leaderboard_path, 'r+') as f:
            leaderboard = json.load(f)

            # Initialize the user's entry if not present
            if creator_id not in leaderboard:
                leaderboard[creator_id] = {'points': 0, 'solved': []}

            # Check if the creator has already been awarded points for this thread
            if thread_name not in leaderboard[creator_id]['solved']:
                # Update the leaderboard
                await self.update_leaderboard(creator_id, points, thread_name)

                # Save the updated leaderboard data
                f.seek(0)  # Resets file position to the start
                json.dump(leaderboard, f, indent=4)
                f.truncate()  # Removes leftover data


    thread_name_to_id = {}

    async def build_thread_mapping(self):
        with open(self.json_path, 'r') as f:
            threads_data = json.load(f)
        self.thread_name_to_id = {thread['name']: thread['id'] for thread in threads_data}
        
        # Print the mapping for debugging
        print(f"Thread name to ID mapping: {self.thread_name_to_id}")

        


            
def setup(bot):
    bot.add_cog(Not_This_Again_CTF(bot))
