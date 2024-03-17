import os
from discord.ext import commands
from dotenv import load_dotenv
import interactions

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = interactions.Client(token=TOKEN)

@bot.command(
    name="hello",
    description="This command says hello!"
)
async def hello(ctx: interactions.CommandContext):
    await ctx.send("Hello!")

bot.start()
