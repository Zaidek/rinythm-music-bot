# IMPORT DISCORD LIBRARIES #
import discord
from discord.ext import commands

# IMPORT STANDARD LIBRARIES #
import numpy as np
import os
import youtube_dl
import asyncio
import re


# INITALISE BOT COMMANDS #
bot = commands.Bot(command_prefix="RIN")

# GLOBAL VARIABLES #
song_queue = []

youtube_download_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'ignoreerrors': False,
    'no_warnings': True,
    'default_search': 'auto',
    'outtmpl': '%(id)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

ffmpeg_options = {
    'options': '-x'
}

connection = None

# COMMANDS #

# COMMAND TO PLAY OR QUEUE GIVEN SONG #
@bot.command()
async def play(context):

    global connection

     # GET MESSAGE CONTEXT #
    author = context.author
    text_channel = context.channel
    guild = text_channel.guild
    message = context.message

    # JOIN VOICE CHANNEL IF NOT ALREADY IN #
    try:
        voice_channel = author.voice.channel
        if voice_channel:
            await join_voice_channel(voice_channel, text_channel, guild)    
    except discord.errors.ClientException:
        print("Client Exception has Occured")

    #GET URL #
    message_url = message.content.strip('RINplay ')

    # APPEND TO QUEUE #
    (filename, title) = extract_url_data(message_url)
    song_queue.append((filename, title))

    # PLAY FIRST SONG #
    if len(song_queue) == 1 and not connection.is_playing():
        first_song = song_queue.pop()
        await context.send("Now playing: {0}".format(first_song[1]))
        connection.play(discord.FFmpegPCMAudio(source = first_song[0]), after = get_next_song)


# COMMAND TO PRINT OUT CURRENT QUEUE # 
@bot.command()
async def queue(context):
    text_channel = context.channel
    for index in range(len(song_queue)):
        await text_channel.send("{0} - {1}".format((index+1), song_queue[index][1]))

# COMMAND TO SKIP CURRENT SONG PLAYING # 
@bot.command()
async def skip(context):
    global connection
    if not connection.is_playing:
        context.send("There is currently no song playing to skip")
        return
    connection.stop()
    await context.send("Skipping song...")    
    await get_next_song()

# COMMAND TO PAUSE CURRENT SONG PLAYING #
@bot.command()
async def pause(context):
    global connection
    if not connection.is_playing:
        context.send("There is currently no song playing to pause")
        return
    connection.pause()

# COMMAND TO RESUME ANY CURRENTLY PAUSED SONG # 
@bot.command()
async def resume(context):
    global connection
    if connection.is_paused:
        context.send("There is currently no paused song to resume")
        return
    connection.play()



# EVENTS #

# EVENT THAT RUNS ON START UP # 
@bot.event
async def on_ready():
    print("{0.user} has arrived".format(bot))
    in_voice_channel = False

# EVENT THAT RUNS WHEN MESSAGE IS RECIEVED # 
@bot.event
async def on_message(message):
    await bot.process_commands(message)


# HELPER FUNCTIONS #

# FUNCTION TO FETCH AND PLAY NEXT SONG IN QUEUE #
async def get_next_song():
    global connection

    print("next song is playing")

    if len(song_queue) > 0:
        next_song = song_queue.pop()
        #await context.send("Now playing: {0}".format(next_song[1]))
        connection.play(discord.FFmpegPCMAudio(source = next_song[0]), after = get_next_song)
    else: 
        await asyncio.sleep(120)
        if not connection.is_playing():
            await connection.disconnect()
            #await context.send("AFK for too long, bot disconnecting")
            print("hello")

# EXTRACTS INFO FROM GIVEN URL #
def extract_url_data(url):
    with youtube_dl.YoutubeDL(youtube_download_options) as ydl:
        data = ydl.extract_info(url)
        if 'entires' in data:
            data = data['entries'][0]
        filename = "{0}.mp3".format(data['id'])
        title = data['title']
    return (filename, title)

# CONNECTS AND SETS VOICE CHANNEL CONNECTION # 
async def join_voice_channel(voice_channel, text_channel, guild):
    global connection

    connection = await voice_channel.connect(reconnect = True)
    await text_channel.send("Joining Voice Channel")

# ENDS VOICE CHANNEL CONNECTION #
async def leave_voice_channel(voice_channel, text_channel):
    global connection

    await voice_channel.disconnect()
    connection = None
    await text_channel.send("Leaving Voice Channel")

# GET DISCORD TOKEN FROM .ENV #
def get_token():
    token = os.getenv('TOKEN')
    return token

# MAIN FUNCTION #
if __name__ == '__main__':
    bot.run(get_token())