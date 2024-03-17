import discord
from discord.ext import commands
import hashlib
import os

class FileHash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def filehash(self, ctx):
        message = ctx.message
        
        # Check if the message has any attachments
        if message.attachments:
            # Please wait message
            please_wait_embed = discord.Embed(title='Please Wait...', color=discord.Color.blue())
            please_wait_embed.set_thumbnail(url="https://raw.githubusercontent.com/L0WK3Y-IAAN/phreakbot/master/src/img/infophreak-04.png")
            please_wait_embed.set_image(url="https://raw.githubusercontent.com/L0WK3Y-IAAN/phreakbot/master/src/img/infophreak-010-cropped-long.png")
            please_wait_message = await ctx.send(embed=please_wait_embed)
            
            for attachment in message.attachments:
                # Check if the attachment is a file
                if attachment.filename:
                    # Download the file
                    await attachment.save(attachment.filename)
                    # Calculate the hashes
                    sha256_hash = self.hash_file(attachment.filename, hashlib.sha256())
                    md5_hash = self.hash_file(attachment.filename, hashlib.md5())
                    sha1_hash = self.hash_file(attachment.filename, hashlib.sha1())
                    # Create the embedded message
                    embed = discord.Embed(title=f"Hashes of {attachment.filename}", color=discord.Color.green())
                    embed.set_thumbnail(url="https://raw.githubusercontent.com/L0WK3Y-IAAN/phreakbot/master/src/img/infophreak-04.png")
                    embed.set_image(url="https://raw.githubusercontent.com/L0WK3Y-IAAN/phreakbot/master/src/img/infophreak-010-cropped-long.png")
                    embed.add_field(name="MD5", value=f'```{md5_hash}```')
                    embed.add_field(name="SHA1", value=f'```{sha1_hash}```')
                    embed.add_field(name="SHA256", value=f'```{sha256_hash}```')
                    
                    # Adding footer with user's name and avatar
                    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
                    
                    # Send the embedded message
                    await ctx.send(embed=embed)
                    
                    # Remove the file after hashing
                    os.remove(attachment.filename)
            
            # Delete the "Please Wait..." embed message
            await please_wait_message.delete()
        else:
            # If no attachment is found, send an embedded prompt on how to use the command properly
            embed = discord.Embed(title="Error", description="You must attach a file to use this command properly. Example: `!filehash <attachment>`", color=discord.Color.red())
            embed.set_thumbnail(url="https://raw.githubusercontent.com/L0WK3Y-IAAN/phreakbot/master/src/img/infophreak-04.png")
            embed.set_image(url="https://raw.githubusercontent.com/L0WK3Y-IAAN/phreakbot/master/src/img/infophreak-010-cropped-long.png")
            embed.add_field(name="Note", value="⚠️File size is limited based on your Nitro subscription.⚠️")
            
            # Adding footer with user's name and avatar
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
            
            await ctx.send(embed=embed)

    def hash_file(self, filename, hasher):
        # Open the file in binary mode and read its content
        with open(filename, 'rb') as f:
            # Calculate the hash of the file content
            while chunk := f.read(4096):  # Read the file in chunks to conserve memory
                hasher.update(chunk)
        # Return the hexadecimal digest of the hash
        return hasher.hexdigest()

def setup(bot):
    bot.add_cog(FileHash(bot))
