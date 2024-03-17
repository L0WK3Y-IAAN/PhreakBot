import os
import discord
import json
import feedparser
import asyncio
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()
TOKEN: str = os.getenv('DISCORD_TOKEN')

# Initialize Discord client
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Ensure your bot has message content intent enabled
client = discord.Client(intents=intents)

# Define RSS feed URLs and their corresponding thread IDs
feed_data = {
    'TheHackersNews': {
        'url': 'https://feeds.feedburner.com/TheHackersNews',
        'thread_id': 1216558371793141912
    },
    'TalosIntelligence': {
        'url': 'https://blog.talosintelligence.com/rss/',
        'thread_id': 1216558371793141912
    }
}

posted_entry_ids: Dict[str, List[str]] = {}

def load_posted_entry_ids() -> Dict[str, List[str]]:
    try:
        with open('cogs/news/posted_entry_ids.json', 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        # If the file doesn't exist, create an empty dictionary
        return {}
    except json.JSONDecodeError:
        # If the file exists but is empty or contains invalid JSON, return an empty dictionary
        return {}

def save_posted_entry_ids() -> None:
    with open('cogs/news/posted_entry_ids.json', 'w') as f:
        json.dump(posted_entry_ids, f)

async def fetch_feed(feed_url: str) -> List:
    # Parse the RSS feed
    feed = feedparser.parse(feed_url)
    return feed.entries

async def post_feed_entries(feed_name: str, feed_url: str, thread_id: int) -> None:
    global posted_entry_ids
    # Fetch feed entries
    entries = await fetch_feed(feed_url)

    # Load posted entry IDs
    posted_entry_ids = load_posted_entry_ids()

    # Filter out entries that have already been posted
    new_entries = [entry for entry in entries if entry.id not in posted_entry_ids.get(feed_name, [])]

    # Post each new feed entry as an embedded message
    for entry in new_entries:
        embed = discord.Embed(title=entry.title, description=entry.summary, url=entry.link, color=discord.Color.blue())
        # Check if the entry has an image in enclosure with type "image/jpeg"
        for enclosure in entry.get('enclosures', []):
            if enclosure.get('type') == 'image/jpeg':
                embed.set_image(url=enclosure.get('href'))
                break
        # Check if the entry has an image in media:content tag with medium="image"
        for media_content in entry.get('media_content', []):
            if media_content.get('medium') == 'image':
                embed.set_image(url=media_content.get('url'))
                break
        # Set the publication date as the embed footer
        embed.set_footer(text=f"Published on {entry.published}")
        # Set the author information
        if 'author' in entry:
            embed.set_author(name=entry.author)
        channel = await client.fetch_channel(thread_id)
        await channel.send(embed=embed)

        # Add the entry ID to the list of posted entry IDs
        posted_entry_ids.setdefault(feed_name, []).append(entry.id)
    # Save posted entry IDs to file
    save_posted_entry_ids()


@client.event
async def on_ready() -> None:
    print('Logged in as {0.user}'.format(client))

    # Post feed entries for each feed initially
    for feed_name, data in feed_data.items():
        await post_feed_entries(feed_name, data['url'], data['thread_id'])

    # Schedule fetching and posting of feed entries for each feed every hour
    while True:
        await asyncio.sleep(3)  # 3600 seconds = 1 hour
        print("Fetching RSS feed entries...")
        for feed_name, data in feed_data.items():
            await post_feed_entries(feed_name, data['url'], data['thread_id'])

# Run the bot
client.run(TOKEN)
