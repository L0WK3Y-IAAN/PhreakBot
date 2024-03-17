import discord
from discord.ext import commands


class DelMsg(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='delmsg')
    async def delete_messages(self, ctx: commands.Context, amount: int):
        if ctx.author.guild_permissions.manage_messages:
            try:
                # Delete the specified number of messages
                deleted = await ctx.channel.purge(limit=amount)
                # Send a confirmation message
                await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=5)
            except discord.NotFound:
                # Handle the case where the interaction is not found
                print("Interaction not found. Unable to send message.")
        else:
            # Send a message if the user doesn't have permissions
            await ctx.send("You don't have permission to use this command.")

def setup(bot):
    bot.add_cog(DelMsg(bot))
