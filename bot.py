print("Inizializing!")

import discord
from discord.ext import commands
from datetime import datetime
import random
import re
import asyncio
import os
import json
import io

async def determine_prefix(bot, msg):
    prefix = "-"
    if msg.guild: #if message is in a guild
        prefix = guilds[msg.guild.id].prefix
    return commands.when_mentioned_or(prefix)(bot, msg)
bot = commands.Bot(command_prefix=determine_prefix)
bot.remove_command('help') #removes the prebuilt help command

messages = ["God fucking damn it, {0}", "Fuck you, {0}", "Leave me alone, I swear to god. You're so fucking annoying and it pisses me off, {0}", "FUCK OFF! {0}", "Pleeease bother someone else oh my fucking god, {0}", "I hope you actually fucking die, {0}"]
guilds = {}

class Server(object):
    def __init__(self, j):
        self.__dict__ = json.load(j)

def createdefault(guild):
    disguild = bot.get_guild(guild)
    with open(str(guild)+".json", "w") as jfile:
        try:
            json.dump({"talk":True, "prefix":"-", "adminrole":disguild.default_role.id, "freq":20, "whitelisted":[disguild.system_channel.id], "log":False, "lchannel":disguild.system_channel.id, "listmax":80, "phrases":["Hi!"]}, jfile)
        except: #if there is no system channel
            json.dump({"talk":True, "prefix":"-", "adminrole":disguild.default_role.id, "freq":20, "whitelisted":[disguild.text_channels[0].id], "log":False, "lchannel":disguild.text_channels[0].id, "listmax":80, "phrases":["Hi!"]}, jfile)
    with open(str(guild)+".json") as jfile:
        guilds[guild] = Server(jfile)

def write(ctx):
    with open(str(ctx.guild.id)+".json", "w") as jfile:
        json.dump(guilds[ctx.guild.id].__dict__, jfile)

@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None

async def admin(ctx):
    if ctx.author.top_role >= ctx.guild.get_role(guilds[ctx.guild.id].adminrole):
        return True
    return False

async def owner(ctx):
    if ctx.author.id == ctx.guild.owner.id:
        return True
    return False

@bot.event
async def on_ready():
    servers = [guild.id for guild in await bot.fetch_guilds().flatten()]
    for guild in servers:
        try:
            with io.open(str(guild)+".json", encoding="utf-8") as jfile:
                guilds[guild] = Server(jfile)
        except FileNotFoundError:
            createdefault(guild)
            print("Remade files for:", bot.get_guild(guild).name)
    print('Here we go again {0.user}'.format(bot))

@bot.event
async def on_guild_join(guild):
    createdefault(guild)
    print("[{0}] Joined server: '".format(datetime.now().time())+guild.name+"' and created files!")
    await guild.get_channel(guilds[guild.id].lchannel).send("Hi, i'm {0}! Please use `-adminset` to set the admin role and `-prefix` to change my prefix! Additionally, you can mention me or use the prefix to start commands! Use {0} help or `-help` for more info.".format(bot.user.mention))

@bot.event
async def on_guild_remove(guild):
    os.remove(str(guild.id)+".json")
    del guilds[guild.id] #not sure if removing the class from the dictionary will actually remove  the class from memory, but who knows.
    print("[{0}] Left server '".format(datetime.now().time())+guild.name+"' ;(")

@bot.event
async def on_message(message):
    phrases = guilds[message.guild.id].phrases
    content = message.content
    if message.author == bot.user:
        return
    if content.startswith((":", ";", "~", "-", "+", "=", ".", ",", "!", "$", "&", "^", "?", bot.user.mention, "".join(["<@!", str(bot.user.id), ">"]))): #ignores commands for every bot in a server, this isn't just brute-force
        await bot.process_commands(message)
        return #don't want it to continue after running a command
    if message.channel.id in guilds[message.guild.id].whitelisted:
        if random.randint(1,10) == 10:
            if "<@" in message.content:
                message.content = re.sub("<[^>]+>", "{0}", message.content)

            content.replace("@everyone", "")
            content.replace("@here", "")
                    
            if message.attachments != []:
                content = content+" "+message.attachments[0].url

            " ".join(message.content.split()) #removes double or more spaces
            if content == "" or content == "** **" or content == "*** ***": # these are all the same message basically, just a blank message.
                content = "_ _"
                    
            if content in phrases:
                print("[{0}] in '{1}':".format(datetime.now().time(), message.guild.name), content, "--- is already in phrases!")
                return

            phrases.append(content)
            while len(phrases) > guilds[message.guild.id].listmax:
                phrases.pop(0)
                    
            write(message)
            print("[{0}] New phrase added in '{1}':".format(datetime.now().time(), message.guild.name), content)
            if guilds[message.guild.id].log:
                await message.guild.get_channel(guilds[message.guild.id].lchannel).send("```New phrase added: "+content+"```")
            return
                
        if guilds[message.guild.id].talk and random.randint(1, guilds[message.guild.id].freq) == guilds[message.guild.id].freq:
            await message.channel.send(random.choice(phrases).format(message.author.mention)) #replaces any flags with things like mentions or line breaks

@bot.event
async def on_command_error(ctx, err):
    if isinstance(err, commands.CheckFailure):
        await ctx.send("Invalid permissions!") 
    elif isinstance(err, commands.CommandNotFound):
        await ctx.send("Command not found! Try `{0}help` for a list of proper commands.".format(guilds[ctx.guild.id].prefix))
    elif isinstance(err, commands.MissingRequiredArgument):
        await ctx.send("This command requires more arguments!")

@bot.command()
async def hi(ctx):
    await ctx.send(random.choice(messages).format(ctx.author.mention))

@bot.command()
async def hug(ctx):
    await ctx.send(":flushed:")

@bot.command()
async def lamp(ctx):
    await ctx.send("Lämp https://tenor.com/view/mothpit-gif-4889422")

@bot.command()
async def moth(ctx):
    await ctx.send("https://media.discordapp.net/attachments/660725993886973967/665234015825035274/tumblr_inline_pigyc2pVCu1t2g1uk_500.gif")

@bot.command()
async def help(ctx):
    await ctx.send("PREFIX: {0} or ping\nCommands are listed here: https://github.com/kurpingspace2/kractl/wiki/Commands".format(guilds[ctx.guild.id].prefix))

@bot.command()
@commands.check(admin)
async def speak(ctx):
    guilds[ctx.guild.id].talk = True
    write(ctx)
    await ctx.send(random.choice(guilds[ctx.guild.id].phrases).format(ctx.author.mention))
    await ctx.message.delete()

@bot.command()
async def shutup(ctx):
    if await admin(ctx):
        guilds[ctx.guild.id].talk = False
        write(ctx)
        await ctx.send("Okay... :(")
    else:
        await ctx.send("No >:(")

@bot.command()
@commands.check(admin)
async def prefix(ctx, newprefix):
    if len(newprefix) == 1 and newprefix in ":;~-+=.,!$&^?":
        guilds[ctx.guild.id].prefix = newprefix
        write(ctx)
        await ctx.send("Prefix set to: {0}".format(newprefix))
    else:
        await ctx.send("Invalid prefix! Avaliable prefixes: `:;~-+=.,!$&^?`")

@bot.command()
@commands.check(owner)
async def adminset(ctx, role):
    if role == "?":
        await ctx.send("Admin role is: "+ctx.guild.get_role(guilds[ctx.guild.id].adminrole).mention)
        return
    try:
        role = int(role.strip("<@&>"))
    except ValueError:
        await ctx.send("Please give a valid role!")
        return
    if ctx.guild.get_role(role) == None:
        await ctx.send("This role does not exist!")
        return
    guilds[ctx.guild.id].adminrole = role
    write(ctx)
    await ctx.send("Admin role set to: {0}".format(ctx.guild.get_role(role).mention))

@bot.command()
@commands.check(admin) 
async def freq(ctx, freq):
    if freq == "?":
        await ctx.send("Frequency: 1/{0}".format(guilds[ctx.guild.id].freq))
        return
    try:
        freq = int(freq)
    except ValueError:
        await ctx.send("Please input an integer!")
        return
    if freq > 0:
        guilds[ctx.guild.id]["freq"] = freq
        write(ctx)
        await ctx.send("Frequency set to 1/{0}!".format(freq))
    else:
        await ctx.send("Please input a number higher than `0`!")

@bot.command()
@commands.check(admin) 
async def whitelist(ctx, flag, *args):
    if flag == "l":
        await ctx.send("Whitelisted channels: "+str(" ".join([ctx.guild.get_channel(textchannel).mention for textchannel in guilds[ctx.guild.id].whitelisted])))
        return
    try:
        channel = int(args[0].strip("<#>"))
    except IndexError:
        await ctx.send("Please insert a channel after flag!")
        return
    except ValueError:
        await ctx.send("Please mention a channel or give channel ID!")
        return
    if flag == "a":
        if ctx.guild.get_channel(channel) == None:
            await ctx.send("This channel does not exist!")
        elif channel in guilds[ctx.guild.id].whitelisted:
            await ctx.send("This channel is already whitelisted!")
        else:
            guilds[ctx.guild.id].whitelisted.append(channel)
            write(ctx)
            await ctx.send("Added channel to whitelist!")
    elif flag == "rm":
        try:
            guilds[ctx.guild.id].whitelisted.remove(channel)
        except ValueError:
            await ctx.send("Could not find that in the whitelist!")
            return
        write(ctx)
        await ctx.send("Channel removed!")
    else:
        await ctx.send("Unknown flag! Flags are: `a, rm, l`")

@bot.command()
@commands.check(admin) 
async def log(ctx, flag, *args):
    if flag == "n":
        guilds[ctx.guild.id].log = False
        write(ctx)
        await ctx.send("No-longer logging phrases!")
        return
    try:
        channel = int(args[0].strip("<#>"))
    except ValueError:
        await ctx.send("Please mention a channel or give channel ID!")
        return
    except IndexError:
        await ctx.send("Please insert a channel after flag!")
        return
    if flag == "y":
        if ctx.guild.get_channel(channel) == None:
            await ctx.send("This channel does not exist!")
            return
        elif channel in guilds[ctx.guild.id].whitelisted:
            await ctx.send("It is not recommended to output logs in a whitelisted channel. And it's not as funny. React above to continue.")
        else:
            await ctx.send("It's not as funny when you log phrases. React above to continue.")
        await ctx.message.add_reaction(u"\U0001F44D")
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == u"\U0001F44D"
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=10.0, check=check) #i have no clue what is happening here
        except asyncio.TimeoutError:
            await ctx.send("Thank you for not logging phrases!")
        else:
            guilds[ctx.guild.id].log = True
            guilds[ctx.guild.id].lchannel = channel
            write(ctx)
            await ctx.send("Logging channel set!")
            await ctx.guild.get_channel(channel).send("```Logs will now appear in this channel. Happy monitoring!```")
    else:
        await ctx.send("Unknown flag! Flags are: `y, n`")

@bot.command()
@commands.check(admin) 
async def list(ctx, flag, *args):
    phrases = guilds[ctx.guild.id].phrases
    if len(args) == 0:
        await ctx.send("This command requires more arguments!")
        return
    if flag == "l":
        cluster = []
        clusters = []
        for index, phrase in enumerate(phrases):
            previous = cluster.copy()
            cluster.append("{0}: ".format(index+1)+phrase+"\n")
            if len("```"+"".join(cluster)+"```") > 2000:
                clusters.append("```"+"".join(previous)+"```")
                cluster = ["{0}: ".format(index+1)+phrase]
        if cluster != []:
            clusters.append("```"+"".join(cluster)+"```") #adds the remainder

        if args[0] == "all":
            for cluster in clusters:
                await ctx.send(cluster)
            return

        if args[0] == "?":
            await ctx.send("`{0}` clusters\n`{1}` phrases".format(len(clusters), len(phrases)))
            return
        try:
            await ctx.send(clusters[int(args[0])-1])
        except ValueError:
            await ctx.send("Please give `a`, `?` or an integer!")
        except IndexError:
            await ctx.send("This does cluster does not exist!")
        return
    
    elif flag == "rm":
        for index in args:
            try:
                index = int(index)-1
                try:
                    phrase = phrases[index] #instead of saying deleted first, it will delete first, then if it fails, it will show an error.
                    phrases.pop(index)
                    await ctx.send("Deleted phrase: `"+phrase+"`")
                except IndexError:
                    await ctx.send("Cannot find `{0}` in the list!".format(index))
            except ValueError:
                await ctx.send("`{0}` isn't an integer".format(index))
        
    elif flag == "a":
        phrases.append(args[0].strip())
        while len(phrases) > guilds[ctx.guild.id].listmax:
            phrases.pop(0)
        await ctx.send("Added phrase!")
        
    elif flag == "max":
        if args[0] == "?":
            await ctx.send("List maximum is: `"+str(guilds[ctx.guild.id].listmax)+"`")
            return
        try:
            maximum = int(args[0])
        except ValueError:
            await ctx.send("Please input an integer!")
            return
        if maximum > 4:
            guilds[ctx.guild.id].listmax = maximum
            await ctx.send("List maximum set to: `"+str(maximum)+"`")
        else:
            await ctx.send("Please input a number higher than `4`")
            
    else:
        await ctx.send("Unknown flag! Flags are: `l, a, rm, max`")
    write(ctx)
        
bot.run("Njg4NTA0NDgwMzY2MzI5OTk1.Xrqomg.PVusxDzDb6FAgdI6RQNfKy8R90Y") #insert the bot token there as str