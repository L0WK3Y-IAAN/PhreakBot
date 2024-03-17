#!/usr/bin/python3

'''
🔴 - Add down detector
🔴 - Add embedded news messages
'''

import os
import base64
import asyncio
import discord
from typing import Final
from openai import OpenAI
from dotenv import load_dotenv
from discord.ext import commands
from cryptography.fernet import Fernet
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import traceback
from datetime import datetime

# Import cogs
from cogs.security_tools.filehash import FileHash
from cogs.server_management.bump_reminder import BumpReminder
from cogs.server_management.deletemsg import DelMsg
from cogs.news.news import NewsFeed



# Function to append error message to a log file
def append_error_to_log(error_message):
    with open("errors/error_log.txt", "a") as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{timestamp} - {error_message}\n")

# Function to handle errors and save them to log file
def handle_error(error_message):
    print(f"🔴 Error: {error_message}")
    append_error_to_log(error_message)


# Function to create error log with current timestamp and user ID as filename
def create_error_log(error_message, user_id):
    handle_error(error_message)
    # You can add additional handling specific to user errors if needed

# Clear terminal
os.system('cls' if os.name == 'nt' else 'clear')

# Ensure the error folder exists
if not os.path.exists("errors"):
    os.makedirs("errors")

# Constants
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
ENCRYPTION_KEY: Final[str] = os.getenv('ENCRYPTION_KEY')
DATABASE: Final[str] = os.getenv('DATABASE')

# Initialize Firestore with your credentials
cred = credentials.Certificate(DATABASE)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Ensure the encryption key is provided
if not ENCRYPTION_KEY:
    raise ValueError("Encryption key not found. Please set the ENCRYPTION_KEY environment variable.")

# Functions for data management
async def load_user_data(user_id):
    doc_ref = db.collection('users').document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return {}

async def save_user_data(user_id, user_data):
    doc_ref = db.collection('users').document(user_id)
    doc_ref.set(user_data)

def encrypt_api_key(api_key, key):
    cipher_suite = Fernet(key)
    encrypted_key = cipher_suite.encrypt(api_key.encode())
    return base64.b64encode(encrypted_key).decode()

def decrypt_api_key(encrypted_api_key, key):
    cipher_suite = Fernet(key)
    encrypted_key = base64.b64decode(encrypted_api_key.encode())
    return cipher_suite.decrypt(encrypted_key).decode()

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Disable default help command
bot.remove_command('help')

# Custom help command
@bot.command(name='help')
async def custom_help(ctx):
    embed = discord.Embed(title="Phreak Bot Help", description="Command List", color=discord.Color.blue())
    embed.add_field(name="@PhreakBot", value="For OpenAI functionality", inline=False)
    # embed.add_field(name="!userinfo [mention]", value="Display information about a user", inline=False)
    embed.set_image(url="https://raw.githubusercontent.com/L0WK3Y-IAAN/PhreakBot/master/src/img/infophreak-010-cropped-long.png")
    embed.set_footer(text="More commands coming soon!")
    await ctx.send(embed=embed)

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'🟢 We have logged in as {bot.user}')
    try:
        print(f"🟢 Cogs loaded!")
    except Exception as e:
        print(f"🔴 {e}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Type !help for a list of commands."))

async def load_cogs():
    for root, dirs, files in os.walk('./cogs'):
        for filename in files:
            if filename.endswith('.py'):
                # Calculate the relative path from the cogs directory
                relative_path = os.path.relpath(os.path.join(root, filename), start='./cogs')
                # Convert the path separator to dots for module import
                module_path = os.path.splitext(relative_path)[0].replace(os.path.sep, '.')
                # Load the extension
                try:
                    await bot.add_cog(FileHash(bot))
                    await bot.add_cog(BumpReminder(bot))
                    await bot.add_cog(DelMsg(bot))
                    await bot.add_cog(NewsFeed(bot))
                    await bot.load_extension(f'cogs.{module_path}')
                except Exception as e:
                    print(f"Failed to load extension '{module_path}': {e}")


# Event: Message received
@bot.event
async def on_message(message):
    try:
        if bot.user.mentioned_in(message):
            prompt = message.content.replace(f'<@!{bot.user.id}>', '').strip()
            user_id = str(message.author.id)
            user_data = await load_user_data(user_id)

            if not user_data:
                await message.author.send("Please provide your OpenAI API key to use the OpenAI functionality.")
                try:
                    api_key_message = await bot.wait_for(
                        'message',
                        timeout=120,
                        check=lambda m: m.author == message.author and m.channel.type == discord.ChannelType.private
                    )
                    # Check if the provided API key starts with "sk-"
                    if not api_key_message.content.startswith("sk-"):
                        await message.author.send("Please provide a valid OpenAI API key. It should start with 'sk-'.\nPlease ping me in the InfoPhreak Discord server, and try again!")
                        return
                    encrypted_api_key = encrypt_api_key(api_key_message.content, ENCRYPTION_KEY)
                    user_data = {'encrypted_openai_api_key': encrypted_api_key}
                    await save_user_data(user_id, user_data)
                except asyncio.TimeoutError:
                    await message.author.send("You did not provide an API key within the time limit.\nPlease ping me in the InfoPhreak Discord server, and try again!")
                    return

            encrypted_api_key = user_data.get('encrypted_openai_api_key')
            openai_api_key = decrypt_api_key(encrypted_api_key, ENCRYPTION_KEY)
            
            channel = message.channel
            please_wait_embed = discord.Embed(title='Thinking...', color=discord.Color.blue())
            please_wait_embed.set_thumbnail(url="https://raw.githubusercontent.com/L0WK3Y-IAAN/phreakbot/master/src/img/infophreak-04.png")
            please_wait_message = await channel.send(embed=please_wait_embed)

            try:
                # Initialize OpenAI client with the decrypted API key
                client = OpenAI(api_key=openai_api_key)
                
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
           
                response = completion.choices[0].message.content

                # If response exceeds 2000 characters, save it to a text file and send the file instead
                if len(response) > 2000:
                    with open('response.txt', 'w') as file:
                        file.write(response)
                    await message.channel.send("The response is too long. Here is the text file:", file=discord.File('response.txt'))
                    os.remove('response.txt')
                else:
                    await message.channel.send(response)

            except Exception as e:
                error_message = traceback.format_exc()
                create_error_log(error_message, user_id)
                # await message.author.send("An error occurred while processing your request. Here is the error log: \nPlease send this log to the InfoPhreak Discord Tech Support channel to receive further assistance! https://discord.gg/xQSS2dKc8F", file=discord.File(error_message, user_id))
                # Check if error message contains "'Incorrect API key provided:"
                if "Incorrect API key provided" or "invalid_api_key" in error_message:
                    await message.author.send("Please provide a valid OpenAI API key.\nEx: sk-... ")
                    print("🔴 Removing user from the database due to invalid API key.")
                    # Remove user from database
                    await remove_user(user_id)

            await please_wait_message.delete()

    except Exception as e:
        error_message = f"An error occurred while processing your request: {str(e)}"
        create_error_log(error_message, message.author.id)
        await message.channel.send("An error occurred while processing your request. The support team has been notified.")
        print(f"🔴 Error: {error_message}")

    await bot.process_commands(message)
    pass

async def remove_user(user_id):
    doc_ref = db.collection('users').document(user_id)
    await doc_ref.delete().to_dict()

async def main():
    try:
        await load_cogs()
        await bot.start(TOKEN)
    finally:
        await bot.close()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\n🔴 Bot shutting down...")
