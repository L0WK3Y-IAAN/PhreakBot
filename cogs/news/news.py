import discord
import json
import feedparser
import asyncio
from typing import Dict, List
from discord.ext import commands


class NewsFeed(commands.Cog):
    def __init__(self, client):
        self.client = client

        # Define RSS feed URLs and their corresponding thread IDs
        self.feed_data = {
            'TheHackersNews': {
                'url': 'https://feeds.feedburner.com/TheHackersNews',
                'thread_id': 1216558371793141912
            },
            'TalosIntelligence': {
                'url': 'https://blog.talosintelligence.com/rss/',
                'thread_id': 1216558336875565077
            },
            'ExploitDB': {
                'url': 'https://www.exploit-db.com/rss.xml',
                'thread_id': 1216986351950630973
            }
        }

        self.posted_entry_ids: Dict[str, List[str]] = {}

    def load_posted_entry_ids(self) -> Dict[str, List[str]]:
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

    def save_posted_entry_ids(self) -> None:
        with open('cogs/news/posted_entry_ids.json', 'w') as f:
            json.dump(self.posted_entry_ids, f)

    async def fetch_feed(self, feed_url: str) -> List:
        # Parse the RSS feed
        feed = feedparser.parse(feed_url)
        return feed.entries

    async def post_feed_entries(self, feed_name: str, feed_url: str, thread_id: int) -> None:
        # Fetch feed entries
        entries = await self.fetch_feed(feed_url)

        # Load posted entry IDs
        self.posted_entry_ids = self.load_posted_entry_ids()

        # Filter out entries that have already been posted
        new_entries = [entry for entry in entries if entry.id not in self.posted_entry_ids.get(feed_name, [])]

        # Sort new entries by publication date (oldest to newest)
        new_entries.sort(key=lambda entry: entry.published_parsed)

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
            channel = await self.client.fetch_channel(thread_id)
            await channel.send(embed=embed)
            # Add the entry ID to the list of posted entry IDs
            self.posted_entry_ids.setdefault(feed_name, []).append(entry.id)
        # Save posted entry IDs to file
        self.save_posted_entry_ids()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print('🔵 NewsFeed cog is ready!')

        # Post feed entries for each feed initially
        for feed_name, data in self.feed_data.items():
            await self.post_feed_entries(feed_name, data['url'], data['thread_id'])

        # Schedule fetching and posting of feed entries for each feed every hour
        while True:
            await asyncio.sleep(3600)  # 3600 seconds = 1 hour
            for feed_name, data in self.feed_data.items():
                await self.post_feed_entries(feed_name, data['url'], data['thread_id'])

# Setup function to add the cog to the bot
def setup(client):
    client.add_cog(NewsFeed(client))
