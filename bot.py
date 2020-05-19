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
    prefix = dpfx
    if msg.guild: #if message is in a guild
        prefix = guilds[msg.guild.id].prefix
    return commands.when_mentioned_or(prefix)(bot, msg)
bot = commands.Bot(command_prefix=determine_prefix)
bot.remove_command('help') #removes the prebuilt help command

messages = ["God fucking damn it, {0}", "Fuck you, {0}", "Leave me alone, I swear to god. You're so fucking annoying and it pisses me off, {0}", "FUCK OFF! {0}", "Pleeease bother someone else oh my fucking god, {0}", "I hope you actually fucking die, {0}"]
guilds = {}
dpfx = "-" #just so i can change the default prefix with ease

class Server(object):
    def __init__(self, j):
        self.__dict__ = json.load(j)

def createdefault(guild): #change default prefix to ^ as soon as possible
    with open(str(guild.id)+".json", "w") as jfile:
        try:
            json.dump({"talk":True, "prefix":dpfx, "adminrole":guild.default_role.id, "freq":20, "whitelisted":[guild.system_channel.id], "log":False, "lchannel":guild.system_channel.id, "listmax":80, "learn":10, "phrases":["Hi!"]}, jfile)
        except: #if there is no system channel
            json.dump({"talk":True, "prefix":dpfx, "adminrole":guild.default_role.id, "freq":20, "whitelisted":[guild.text_channels[0].id], "log":False, "lchannel":guild.text_channels[0].id, "listmax":80, "learn":10, "phrases":["Hi!"]}, jfile)
    with open(str(guild.id)+".json") as jfile:
        guilds[guild.id] = Server(jfile)

def write(ctx):
    with open(str(ctx.guild.id)+".json", "w") as jfile:
        json.dump(guilds[ctx.guild.id].__dict__, jfile)

async def admin(ctx):
    if ctx.author.top_role >= ctx.guild.get_role(guilds[ctx.guild.id].adminrole):
        return True
    return False

async def owner(ctx):
    if ctx.author.id == ctx.guild.owner.id:
        return True
    return False

@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None # this is kinda useless but whatever

@bot.event
async def on_ready():
    servers = [guild for guild in await bot.fetch_guilds().flatten()]
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(servers)} servers"))
    for guild in servers:
        try:
            with io.open(str(guild.id)+".json", encoding="utf-8") as jfile:
                guilds[guild.id] = Server(jfile)
        except FileNotFoundError:
            createdefault(guild)
            print("Remade files for:", guild.name)
    print(f"Here we go again {bot.user}")

@bot.event
async def on_guild_join(guild):
    createdefault(guild)
    print(f"[{datetime.now().time()}] Joined server: '{guild.name}' and created files!")
    await guild.get_channel(guilds[guild.id].lchannel).send(f"Hi, i'm {bot.user.mention}! Please use `-adminset` to set the admin role and `-prefix` to change my prefix! Additionally, you can mention me or use the prefix to start commands! Use {bot.user.mention} help or `-help` for more info.")
    servers = [guild for guild in await bot.fetch_guilds().flatten()]
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(servers)} servers"))

@bot.event
async def on_guild_remove(guild):
    os.remove(str(guild.id)+".json")
    del guilds[guild.id] #not sure if removing the class from the dictionary will actually remove  the class from memory, but who knows.
    print(f"[{datetime.now().time()}] Left server '{guild.name}' ;(")
    servers = [guild for guild in await bot.fetch_guilds().flatten()]
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(servers)} servers"))

@bot.event
async def on_message(message):
    phrases = guilds[message.guild.id].phrases
    content = message.content
    if message.author == bot.user:
        return
    if content.startswith((":", ";", "~", "-", "+", "=", ".", ",", "!", "$", "&", "^", "?", "[", "]", "'", "%", "£", bot.user.mention, "".join(["<@!", str(bot.user.id), ">"]))): #ignores commands for every bot in a server, this isn't just brute-force
        if not content.startswith(guilds[message.guild.id].prefix+guilds[message.guild.id].prefix): #if the prefix is not called twice
            await bot.process_commands(message)
        return #don't want it to continue after running a command
    if message.channel.id in guilds[message.guild.id].whitelisted:
        if random.randint(1, guilds[message.guild.id].learn) == guilds[message.guild.id].learn:
            if "<@" in content:
                content = re.sub("<[^>]+>", "{0}", content)

            content.replace("@everyone", "")
            content.replace("@here", "")
                    
            if message.attachments != []:
                content = content+" "+message.attachments[0].url

            " ".join(message.content.split()) #removes double or more spaces
            if content == "" or content == "** **" or content == "*** ***": # these are all the same message basically, just a blank message.
                content = "_ _"
                    
            if content in phrases:
                print(f"[{datetime.now().time()}] in '{message.guild.name}': {content} --- is already in phrases!")
                return

            phrases.append(content)
            while len(phrases) > guilds[message.guild.id].listmax:
                phrases.pop(0)
                    
            write(message)
            print(f"[{datetime.now().time()}] New phrase added in '{message.guild.name}':", content)
            if guilds[message.guild.id].log:
                await message.guild.get_channel(guilds[message.guild.id].lchannel).send("```New phrase added: "+content+"```")
            return
                
        if guilds[message.guild.id].talk and random.randint(1, guilds[message.guild.id].freq) == guilds[message.guild.id].freq:
            await message.channel.send(random.choice(phrases).format(message.author.mention)) #replaces any flags with things like mentions 

@bot.event
async def on_command_error(ctx, err):
    if isinstance(err, commands.CheckFailure):
        await ctx.send("Invalid permissions!") 
    elif isinstance(err, commands.MissingRequiredArgument):
        await ctx.send("This command requires more arguments!")

@bot.command()
async def hi(ctx):
    await ctx.send(random.choice(messages).format(ctx.author.mention))

@bot.command()
async def hug(ctx):
    await ctx.send(":flushed:")

@bot.command()
async def help(ctx):
    await ctx.send(f"PREFIX: {guilds[ctx.guild.id].prefix} or ping\nCommands are listed here: https://github.com/kurpingspace2/kractl/wiki/Commands \nNeed support? https://discord.gg/CXnE5MX")

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
    if len(newprefix) == 1 and newprefix not in "qwertyuiopasdfghjklzxcvbnm1234567890*_~`{<@\\/":
        guilds[ctx.guild.id].prefix = newprefix
        write(ctx)
        await ctx.send("Prefix set to: "+newprefix)
    else:
        await ctx.send("Invalid prefix! Unavaliable prefixes: ```qwertyuiopasdfghjklzxcvbnm1234567890*_~`{<@\\/```")

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
    await ctx.send("Admin role set to: "+ctx.guild.get_role(role).mention)

@bot.command()
@commands.check(admin) 
async def freq(ctx, flag, *args):
    if flag == "?":
        await ctx.send(f"Chance to speak: 1/{guilds[ctx.guild.id].freq}\nChance to learn: 1/{guilds[ctx.guild.id].learn}")
        return
    try:
        freq = args[0]
    except IndexError:
        await ctx.send("This command requires another argument!")
        return
    try:
        freq = int(freq)
    except ValueError:
        await ctx.send("Please input an integer!")
        return
    if not freq > 0:
        await ctx.send("Please input a number higher than `0`!")
        return
    if flag == "s":
        guilds[ctx.guild.id].freq = freq
        write(ctx)
        await ctx.send("Speaking frequency set to 1/"+str(freq))
    elif flag == "l":
        guilds[ctx.guild.id].learn = freq
        write(ctx)
        await ctx.send("Learning frequency set to 1/"+str(freq))
    else:
        await ctx.send("Unknown flag, flags are `s, l, ?`")

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
        await ctx.message.add_reaction("👍")
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == "👍"
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
async def l(ctx, *args):
    phrases = guilds[ctx.guild.id].phrases
    flag = args[0]
    args = list(args)
    args.pop(0)
    cluster = []
    clusters = []
    for index, phrase in enumerate(phrases):
        previous = cluster.copy()
        cluster.append("{0}: ".format(index)+phrase+"\n")
        if len("```"+"".join(cluster)+"```") > 2000:
            clusters.append("```"+"".join(previous)+"```")
            cluster = ["{0}: ".format(index)+phrase]
    if cluster != []:
        clusters.append("```"+"".join(cluster)+"```") #adds the remainder

    try:
        flag = int(flag)
        try:
            await ctx.send(clusters[flag])
        except IndexError:
            await ctx.send("This does cluster does not exist!")
        return
    except ValueError:
        None

    if flag == "?":
        await ctx.send(f"`{len(clusters)}` clusters\n`{len(phrases)}` phrases")

    elif flag == "all":
        for cluster in clusters:
            await ctx.send(cluster)

    elif len(args) == 0:
        await ctx.send("This subcommand requires another argument!")

    elif flag == "rm":
        for index in args:
            try:
                index = int(index)
                try:
                    phrase = phrases[index] #instead of saying deleted first, it will delete first, then if it fails, it will show an error.
                    phrases.pop(index)
                    await ctx.send("Deleted phrase: `"+phrase+"`")
                except IndexError:
                    await ctx.send(f"Cannot find `{index}` in the list!")
            except ValueError:
                await ctx.send(f"`{index}` isn't an integer")
        
    elif flag == "a":
        phrases.append(" ".join(args).strip())
        while len(phrases) > guilds[ctx.guild.id].listmax:
            phrases.pop(0)
        await ctx.send(f"""Added phrase: {" ".join(args).strip()}""")
        
    elif flag == "max":
        if args[0] == "?":
            await ctx.send("List maximum is: `"+str(guilds[ctx.guild.id].listmax)+"`")
            return
        try:
            maximum = int(args[0])
        except ValueError:
            await ctx.send("Please input an integer!")
            return
        if maximum > 0:
            guilds[ctx.guild.id].listmax = maximum
            await ctx.send("List maximum set to: `"+str(maximum)+"`")
        else:
            await ctx.send("Please input a number higher than `0`")

    else:
        await ctx.send("Unknown flag! Flags are: `all, ?, p, a, rm, max` or an integer")
    write(ctx)

with open("token.json") as jfile:
    token = json.load(jfile)
bot.run(token["token"])