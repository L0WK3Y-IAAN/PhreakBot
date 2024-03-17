'''
🔴 - Implement a feature that utilizes OpenAPI functionality when pinging the bot
🔴 - Implement a feature that grabs user's discord ID and checks to see if their OpenAI API key is already stored in the database
🔴 - Implement a feature that asks user for their OpenAI API key when trying to use AI functionality (Have a message sent to their DMs saying "You are attempting you use OpenAPI functionality but have not yet registered your OpenAPI key")
🔴 - Implement a feature that stores user's OpenAI API key in the database and encrypts it and decrypts it when that user is trying to use OpenAI functionality





🟢 - Completed the task
🟡 - Needs attention/Work in progress
🔴 - Not working/Implemented
🔵 - Ideas for the the project
'''


import os
import json
import base64
import asyncio
import discord
from typing import Final
from openai import OpenAI
from dotenv import load_dotenv
from discord.ext import commands
from cryptography.fernet import Fernet

# Load token from env
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
KEY: Final[str] = os.getenv('OPENAI_KEY')

# Load user data from JSON file
def load_user_data():
    try:
        with open('users.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    
def decrypt_api_key(encrypted_api_key, key):
    encrypted_key = base64.b64decode(encrypted_api_key.encode())
    cipher_suite = Fernet(key)
    return cipher_suite.decrypt(encrypted_key).decode()

def save_user_data(user_data):
    with open('users.json', 'w') as file:
        json.dump(user_data, file, indent=4)

def encrypt_api_key(api_key, key):
    cipher_suite = Fernet(key)
    encrypted_key = cipher_suite.encrypt(api_key.encode())
    return base64.b64encode(encrypted_key).decode()



# Generate a random encryption key
encryption_key = Fernet.generate_key()
print (encryption_key)

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
client = OpenAI(api_key=KEY)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    # Check if the message mentions the bot
    if bot.user.mentioned_in(message):
        # Get the user's prompt following the mention
        prompt = message.content.replace(f'<@!{bot.user.id}>', '').strip()
        
        # Get user's Discord ID
        user_id = str(message.author.id)
        
        # Load user data
        user_data = load_user_data()
        
        # Check if user's Discord ID is in the user data
        if user_id not in user_data:
            # If not, send a direct message asking for OpenAI API key
            await message.author.send("Please provide your OpenAI API key.")
            # Wait for the user to respond with their API key
            try:
                api_key_message = await bot.wait_for(
                    'message',
                    timeout=120,  # Timeout after 2 minutes
                    check=lambda m: m.author == message.author and m.channel.type == discord.ChannelType.private
                )
                # Encrypt and add user to the user data with their encrypted API key
                encrypted_api_key = encrypt_api_key(api_key_message.content, encryption_key)
                user_data[user_id] = {'encrypted_openai_api_key': encrypted_api_key}
                save_user_data(user_data)
            except asyncio.TimeoutError:
                await message.author.send("You did not provide an API key within the time limit. Please try again later.")
                return
        
        # Decrypt user's OpenAI API key
        encrypted_api_key = user_data[user_id]['encrypted_openai_api_key']
        openai_api_key = decrypt_api_key(encrypted_api_key, encryption_key)
        
        # Generate a response using OpenAI
        # Use the user input in the chat completion
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            api_key=openai_api_key  # Use user's OpenAI API key
        )
        
        # Send the response
        await message.channel.send(completion.choices[0].message.content)

    # Process commands
    await bot.process_commands(message)

bot.run(TOKEN)
