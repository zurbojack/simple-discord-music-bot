# Discord Music Bot
This repository contains a simple discord music bot written in python that can play any video on youtube, either by passing links or keywords to search on youtube.    

### Library used
The bot is build using python and in particular using the libraries: 
- discord.py
- yt_dlp (a fork of youtube-dl)
- pytube 

I know that discord.py is discontinued, but the features it has are enough for what the bot does.  
### Future 
I had some problems implementing the emptying of the queue, but I solved them using a strange solution that appears to work, but it's pretty ugly.  
So, in the future, I am planning to find a cleaner solution for the queue.  
I am also thinking about migrating the whole bot to javascript, for which there is a currently supported library.

## What do you need to run the bot?
First, you need to install the following things:
- FFmpeg, install it and add it to your system path
- A python installation (I tested only on versione 3.8.5)
- Some python libraries installed: discord.py, yt_dlp, pytube, urllib, re, os, asyncio

Then, you can download the file "bot.py" and insert your discord bot token in the last line of code (remember to invite the bot to your discord server!).

Finally you can run the python script and your bot should appear online on the server. Every command to the bot written in discord corresponds to debug 

## What command do the bot support?
The bot support only songs/audio from youtube. The supported command are:  

| Command       | Aliases           | Description                     | Example           |
| :---          |       :----:      |      :----:                     |            ---:   |
| hi            | N.D.              | bot responds saying hi          | /hi               |
| join          | N.D.              | join your voice channel         | /join             |
| play          | p                 | starts playing a song from yt link or search for the keywords specified, if the bot is playing something the song is added to queue | /play halo beyoncè           |
| skip          | next              | skips the current song and play the next one (if exists) | /skip            |
| song          | current_song      | display the name of the current song | /song             |
| queue         | q, show_queue     | display all the song in queue        | /queue            |
| stop          | N.D.              | disconnect from voice channel        | /stop             |