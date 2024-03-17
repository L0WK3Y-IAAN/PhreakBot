import xml.etree.ElementTree as ET
import discord



'''
Testing
'''

def get_news_embed():
    # XML data
    xml_data = """
    <item>
    <title>Stealthy Zardoor Backdoor Targets Saudi Islamic Charity Organizations</title>
    <description>
    <![CDATA[ An unnamed Islamic non-profit organization in Saudi Arabia has been targeted as part of a stealthy cyber espionage campaign designed to drop a previously undocumented backdoor called&nbsp;Zardoor. Cisco Talos, which discovered the activity in May 2023, said the campaign has likely persisted since at least March 2021, adding it has identified only one compromised target to date, although it's ]]>
    </description>
    <link>https://thehackernews.com/2024/02/stealthy-zardoor-backdoor-targets-saudi.html</link>
    <guid isPermaLink="false">https://thehackernews.com/2024/02/stealthy-zardoor-backdoor-targets-saudi.html</guid>
    <pubDate>Fri, 09 Feb 2024 12:01:00 +0530</pubDate>
    <author>info@thehackernews.com (The Hacker News)</author>
    <enclosure length="12216320" type="image/jpeg" url="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjeEBKWJ4rXJt7j128mhy9BR4McypW_9nzD1KNTIsZ9GV6WnV8nf1CVi0WJevtMtMLQpYT5RjDtxuHNlnJEvGFwy7y2u6c3IrfYSOJRg7HiQ7mHpm-HrN7k_7x8Jv4eeVojlJkhmsunfRnj6qh5OagvHnBf0SNDHFem1GMdJ_hbYDBNDmogbCS0nd1uhHDE/s1600/malware.jpg"/>
    </item>
    """

    # Parse the XML data
    root = ET.fromstring(xml_data)

    # Extract information from the XML
    title = root.find('title').text
    description = root.find('description').text
    link = root.find('link').text
    pub_date = root.find('pubDate').text
    image_url = root.find('.//enclosure').attrib['url']

    # Create an embedded message
    embed = discord.Embed(title=title, url=link, description=description, color=discord.Color.green())
    embed.set_footer(text=f"Published: {pub_date}")
    embed.set_image(url=image_url)

    return embed


