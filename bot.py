import os
import asyncio

import yt_dlp
from pytube import YouTube

import urllib.parse, urllib.request
import re

import discord
from discord import channel
from discord.flags import Intents
from discord.ext import commands

# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# BOT AND YT_DLP OPTIONS

intents = discord.Intents.all()

prefix = "/"

bot = commands.Bot(command_prefix=prefix, description='I am a music bot', intents=intents)

yt_dlp.utils.bug_reports_message = lambda: ''
ytdl_format_options = {'format': 'bestaudio',
                        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
                        'restrictfilenames': True,
                        'no-playlist': True,
                        'nocheckcertificate': True,
                        #'ignoreerrors': False,
                        'ignoreerrors': True,
                        'logtostderr': False,
                        'geo-bypass': True,
                        'quiet': True,
                        'no_warnings': True,
                        'default_search': 'auto',
                        'source_address': '0.0.0.0',
                        'no_color': True,
                        'overwrites': True,
                        'age_limit': 100,
                        'live_from_start': True}

ffmpeg_options = {'options': '-vn -sn'}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# USER-DEFINED CLASSES AND FUNCTION

# class to manage the whole queue and the music playing
class music_player:
    def __init__(self, gid):
        self.guild_id = gid
        self.queue = []
        self.current_song = ""

    async def play(self, ctx, arg):
        # checks if arg is a link or a keywords to search on yt
        if "https" not in arg:
            print(f"PLAY \t| Searching for {arg} on youtube...")

            query_string = urllib.parse.urlencode({"search_query": arg})
            formatUrl = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
            search_results = re.findall(r"watch\?v=(\S{11})", formatUrl.read().decode())
            url = f'https://www.youtube.com/watch?v={search_results[0]}'

            print(f"PLAY \t| Found the result for {arg}")
        else:
            url = arg + ""
            if "youtube" not in arg:
                return

        # song's information extraction
        song_info = ytdl.extract_info(url, download=False)
        song_info = {x:song_info[x] for x in ['url', 'title']}

        print(f"PLAY \t| Added {song_info['title']} to queue")
        await ctx.send(f'Added "{song_info["title"]}" to queue')

        self.queue.append(song_info)

        if not ctx.voice_client.is_playing():
            to_play = discord.FFmpegPCMAudio(song_info["url"], **ffmpeg_options)
            self.current_song = song_info["title"]
            print(f"PLAY \t| Playing {song_info['title']}")
            await ctx.send(f'Now playing: {song_info["title"]}')
            await ctx.voice_client.play(to_play, after=lambda e=None: self.after_playing(ctx, e))

    # for loop does not work, so i used this strange solution below that works but it's pretty ugly

    def after_playing(self, ctx, e):
        self.queue.pop(0)
        if len(self.queue) > 0:
            self.play_next(ctx)
    
    def play_next(self, ctx):
        if len(self.queue) > 0:
            to_play = discord.FFmpegPCMAudio(self.queue[0]["url"], **ffmpeg_options)
            self.current_song = self.queue[0]["title"]
            # asyncio.run_coroutine_threadsafe() used to run function that needs await outside async function
            asyncio.run_coroutine_threadsafe(ctx.send(f'Now playing: {self.queue[0]["title"]}'), bot.loop)
            ctx.voice_client.play(to_play, after=lambda e=None: self.after_playing(ctx, e))


# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# GLOBAL VARIABLES

music_players_dict = {}

# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# BOT CODE

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

# simple hi message
@bot.command()
async def hi(ctx):
    await ctx.send(f"hello {ctx.message.author.name}, I am ready!")

# bot joins the voice channel
@bot.command()
async def join(ctx):
    channel = ctx.message.author.voice.channel 

    if ctx.voice_client == None:
        print("JOIN \t| Connecting to the channel...")
        await channel.connect()
    elif ctx.voice_client.channel != channel:
        print("JOIN \t| Moving to the channel...")
        await ctx.voice_client.move_to(channel)

# display the name of the current song
@bot.command(name='song')
async def current_song(ctx):
    guild_id = ctx.guild.id

    print(f"SHOW Q \t| Current song: {music_players_dict[guild_id].current_song}")
    await ctx.send(f'Now playing {music_players_dict[guild_id].current_song}')

# display all the song in queue
@bot.command(name='queue', aliases=['q'])
async def show_queue(ctx):
    guild_id = ctx.guild.id

    print(f"SHOW Q \t| Queue lenght: {len(music_players_dict[guild_id].queue)}")
    songs = []
    for entry in music_players_dict[guild_id].queue:
        songs.append(entry["title"])

    await ctx.send("\n".join([f'{i}. {s}' for i, s in enumerate(songs)]))

# skip the current song
@bot.command(name='skip', aliases=['next'])
async def skip(ctx):
    guild_id = ctx.guild.id

    if ctx.voice_client.is_playing():
        if len(music_players_dict[guild_id].queue) > 1:
            ctx.voice_client.stop()  # this calls after_playing
        else:
            await ctx.send('No more songs in the queue!')

# the bot leaves the channel
@bot.command()
async def stop(ctx):
    print("STOP \t| Leaving the channel...")
    await ctx.voice_client.disconnect()

# add a song to queue, you can pass both a link or keywords
@bot.command(name='play', aliases=['p'])
async def play(ctx, arg):

    guild_id = ctx.guild.id
    channel = ctx.message.author.voice.channel 

    # one bot per guild
    if guild_id not in music_players_dict:
        await channel.connect()
        if  ctx.voice_client.is_connected():
            music_players_dict[guild_id] = music_player(guild_id)
            print("JOIN \t| Connecting to the channel...")
    else:
        await join(ctx)

    await music_players_dict[guild_id].play(ctx, arg)

# start the bot
bot.run('your-discord-token-here', log_handler=None)