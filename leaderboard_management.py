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
intents.guilds = True
intents.members = True
bot = discord.Client(intents=intents)

# Leaderboard file path
leaderboard_file_path = '.\\misc\\phreakbot challenges\\challenges\\leaderboard.json'

# Store the initial modified time
file_last_modified = os.path.getmtime(leaderboard_file_path)

# Function to determine rank based on points
def determine_rank(points):
    if points < 200:
        return "👶 Noobie"
    elif 200 <= points < 500:
        return "🎓 Novice"
    elif 500 <= points < 1000:
        return "🌟 Apprentice"
    elif 1000 <= points < 1500:
        return "🔥 Adept"
    elif 1500 <= points < 2000:
        return "⚔️ Veteran"
    elif 2000 <= points < 3000:
        return "🛡️ Guardian"
    elif 3000 <= points < 4000:
        return "👑 Elite"
    elif 4000 <= points < 8000:
        return "👽 Hacker"
    elif 8000 <= points < 12000:
        return "💫 Omni"
    elif 12000 <= points < 15000:
        return "🧙‍♂️ Wizard"
    elif 15000 <= points < 17000:
        return "🏅 Master"
    elif 17000 <= points < 20000:
        return "🧘‍♂️ Guru"
    elif points >= 20000:
        return "🌌 God"
    else:
        return "👁️ The Chosen One"

async def update_leaderboard_embed():
    global file_last_modified
    await bot.wait_until_ready()
    leaderboard_channel_id = 1217756961160822854  # The channel where you want to send the leaderboard

    while not bot.is_closed():
        try:
            current_modified_time = os.path.getmtime(leaderboard_file_path)
            if current_modified_time != file_last_modified:
                file_last_modified = current_modified_time

                with open(leaderboard_file_path, 'r') as f:
                    leaderboard = json.load(f)

                guild = bot.get_guild(1174628900001824779)
                if guild is None:
                    print("Guild not found")
                    continue

                sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: int(x[1]['points']), reverse=True)
                
                leaderboard_embed = discord.Embed(title="Leaderboard", color=discord.Color.green())
                
                channel = bot.get_channel(leaderboard_channel_id)
                if channel is None:
                    print("Leaderboard channel not found")
                    continue

                leaderboard_embed.clear_fields()
                for index, (user_id, user_data) in enumerate(sorted_leaderboard, start=1):
                    member = await guild.fetch_member(int(user_id))
                    points = int(user_data['points'])  # Ensure points are integers
                    rank = determine_rank(points)  # Use the function to determine rank
                    field_name = f"{index}. {member.display_name} - ✨ {points} points"
                    field_value = rank
                    leaderboard_embed.add_field(name=field_name, value=field_value, inline=False)

                leader_user_id, _ = sorted_leaderboard[0]
                leader_member = await guild.fetch_member(int(leader_user_id))
                leader_avatar_url = str(leader_member.display_avatar.url) if leader_member.display_avatar else str(leader_member.default_avatar.url)
                leaderboard_embed.set_thumbnail(url=leader_avatar_url)
                leaderboard_embed.set_image(url="https://github.com/L0WK3Y-IAAN/PhreakBot/blob/master/src/img/infophreak-27.png?raw=true")

                messages = [msg async for msg in channel.history(limit=10) if msg.author == bot.user and msg.embeds]
                if messages:
                    await messages[0].edit(embed=leaderboard_embed)
                else:
                    await channel.send(embed=leaderboard_embed)

        except Exception as e:
            print(f"An error occurred: {e}")

        await asyncio.sleep(3)  # Sleep for some time before checking again

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    bot.loop.create_task(update_leaderboard_embed())

bot.run(TOKEN)