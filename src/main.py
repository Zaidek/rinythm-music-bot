# IMPORT DISCORD LIBRARIES
import discord
from discord.ext import commands

# IMPORT STANDARD LIBRARIES
import numpy as np
import os
import pafy
import youtube_dl


#INITALISE BOT COMMANDS
bot = commands.Bot(command_prefix="RIN")

# CREATE COMPONENTS CLIENT 
#components_client = discord_components.DiscordComponents(bot)


in_voice_channel = None

youtube_download_options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

@bot.command()
async def play(context):

     # GET MESSAGE CONTEXT
    author = context.author
    text_channel = context.channel
    guild = text_channel.guild
    message = context.message

    # GET VOICE CHANNEL
    try:
        voice_channel = author.voice.channel
        if voice_channel:
            connection = await join_voice_channel(voice_channel, text_channel)
            
    except discord.errors.ClientException:
        print("oh shit")


    message_url = message.content.strip('RINplay ')
    print(message_url)
    with youtube_dl.YoutubeDL(youtube_download_options) as ydl:
        audio = ydl.download([message_url])

    await text_channel.send(message_url)
    connection.play(source = audio)

       

    

async def join_voice_channel(voice_channel, text_channel):
    connection = await voice_channel.connect(reconnect = True)
    await text_channel.send("Joining Voice Channel")
    return connection

async def leave_voice_channel(voice_channel, text_channel):
    await voice_channel.disconnect()
    await text_channel.send("Leaving Voice Channel")

@bot.event
async def on_ready():
    print("{0.user} has arrived".format(bot))
    in_voice_channel = False

@bot.event
async def on_message(message):
    await bot.process_commands(message)



def get_token():
    token = os.getenv('TOKEN')
    return token

if __name__ == '__main__':
    # RUN EMAILIA
    bot.run(get_token())