print("Inizializing!")

import discord
from discord.ext import commands
from datetime import datetime
import random
import re
import emoji
import asyncio
import os

messages = ["God fucking damn it, {0}", "Fuck you, {0}", "Leave me alone, I swear to god. You're so fucking annoying and it pisses me off, {0}", "FUCK OFF! {0}", "Pleeease bother someone else oh my fucking god, {0}", "I hope you actually fucking die, {0}"]
guilds = {}

def changesetting(ctx, line, contents):
    with open("{0}-settings.txt".format(ctx.guild.id)) as file:
        data = file.readlines()
    data[line] = str(contents)+"\n"
    with open("{0}-settings.txt".format(ctx.guild.id), "w") as file:
        file.writelines(data)

class Server:
    def __init__(self, t, prfx, arole, f, white, l, lch, lmx):
        self.talk = t
        self.prefix = prfx
        self.adminrole = arole
        self.freq = f
        self.whitelisted = white
        self.log = l
        self.lchannel = lch
        self.listmax = lmx
        
def setting(guildId):
    if guildId in guilds:
        return guilds[guildId]
    return None

async def determine_prefix(bot, msg):
    prefix = "-"
    if msg.guild: #if message is in a guild
        prefix = setting(msg.guild.id).prefix
    return commands.when_mentioned_or(prefix)(bot, msg)
    
bot = commands.Bot(command_prefix=determine_prefix)
bot.remove_command('help') #removes the prebuilt help command

@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None

async def admin(ctx):
    if ctx.author.top_role >= ctx.guild.get_role(setting(ctx.guild.id).adminrole):
        return True
    return False

async def owner(ctx):
    if ctx.author.id == ctx.guild.owner.id:
        return True
    return False

@bot.event
async def on_ready():
    servers = [str(guild.id)+"-settings.txt" for guild in await bot.fetch_guilds().flatten()]
    for guild in servers:
        try:
            with open(guild) as settings:
                settings = [item.strip() for item in settings.readlines()]
        except FileNotFoundError:
            disguild = bot.get_guild(int(guild.strip("-settings.txt")))
            settings = ["1", "-", str(disguild.default_role.id), "12", str(disguild.system_channel.id), "0", str(disguild.system_channel.id), "40"]
            with open(guild, "w") as file:
                file.write("1\n-\n{0}\n12\n{1}\n0\n{1}\n40".format(disguild.default_role.id, disguild.system_channel.id))
            with open(guild.replace("settings", "think"), "w") as file:
                file.write("Hi!")
        guilds[int(guild.strip("-settings.txt"))] = Server(bool(int(settings[0])), settings[1], int(settings[2]), int(settings[3]), [int(setting) for setting in settings[4].strip("[]").split(", ")], bool(int(settings[5])), int(settings[6]), int(settings[7]))
    print('Here we go again {0.user}'.format(bot))

@bot.event
async def on_guild_join(guild):
    with open("{0}-settings.txt".format(guild.id), "w") as file:
        file.write("1\n-\n{0}\n12\n{1}\n0\n{1}\n40".format(guild.default_role.id, guild.system_channel.id))
    with open("{0}-think.txt".format(guild.id), "w") as file:
        file.write("Hi!")
    guilds[guild.id] = Server(True, "-", guild.default_role.id, 12, [guild.system_channel.id], False, guild.system_channel.id, 40)
    print("[{0}] Joined server: '".format(datetime.now().time())+guild.name+"' and created files!")
    await guild.system_channel.send("Hi, i'm {0}! Please use `-adminset` to set the admin role and `-prefix` to change my prefix! Additionally, you can mention me or use the prefix to start commands! Use {0} help or `-help` for more info.".format(bot.user.mention))

@bot.event
async def on_guild_remove(guild):
    os.remove("{0}-settings.txt".format(guild.id))
    os.remove("{0}-think.txt".format(guild.id))
    print("[{0}] Left server '".format(datetime.now().time())+guild.name+"' ;(")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith((":", ";", "~", "-", "+", "=", ".", ",", "!", "$", "&", "^", "?", bot.user.mention, "".join(["<@!", str(bot.user.id), ">"]))): #ignores commands for every bot in a server, this isn't just brute-force
        await bot.process_commands(message)
        return #don't want it to continue after running a command
    if message.channel.id in setting(message.guild.id).whitelisted:
        with open("{0}-think.txt".format(message.guild.id)) as file:
            phrases = [line.strip() for line in file.readlines()]
        if random.randint(1,10) == 10:
            if "<@" in message.content:
                message.content = re.sub("<[^>]+>", "{0}", message.content)
                    
            if message.attachments != []:
                message.content = message.content+" "+message.attachments[0].url

            if "\n" in message.content:
                message.content = message.content.replace("\n", " ")
            
            " ".join(message.content.split())
            if message.content == "" or message.content == "** **" or message.content == "*** ***":
                message.content = "_ _"
                    
            message.content = emoji.demojize(message.content.strip()) #can't write unicode characters for some reason, gotta convert
            if message.content in phrases:
                print("[{0}] in '{1}':".format(datetime.now().time(), message.guild.name), message.content, "--- is already in phrases!")
                if setting(message.guild.id).log:
                    await message.guild.get_channel(setting(message.guild.id).lchannel).send("```"+message.content+" --- is already in phrases!```")
                return

            phrases.append(message.content)
            while len(phrases) > setting(message.guild.id).listmax:
                phrases.pop(0)
                    
            with open("{0}-think.txt".format(message.guild.id), "w") as phraselist:
                for phrase in phrases:
                    phraselist.write(phrase+"\n")

            print("[{0}] New phrase added in '{1}':".format(datetime.now().time(), message.guild.name), message.content)
            if setting(message.guild.id).log:
                await message.guild.get_channel(setting(message.guild.id).lchannel).send("```New phrase added: "+message.content+"```")
            return
                
        if setting(message.guild.id).talk and random.randint(1, setting(message.guild.id).freq) == setting(message.guild.id).freq:
            await message.channel.send(emoji.emojize(random.choice(phrases).format(message.author.mention))) #turns any emoji back into a unicode character and sends the message

@bot.event
async def on_command_error(ctx, err):
    if isinstance(err, commands.CheckFailure):
        await ctx.send("Invalid permissions!") 
    elif isinstance(err, commands.CommandNotFound):
        await ctx.send("Command not found! Try `{0}help` for a list of proper commands.".format(setting(ctx.guild.id).prefix))

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
    await ctx.send("PREFIX: {0} or ping\nCommands are listed here: https://github.com/kurpingspace2/kractl/wiki/Commands".format(setting(ctx.guild.id).prefix))

@bot.command()
@commands.check(admin)
async def speak(ctx):
    setting(ctx.guild.id).talk = True
    changesetting(ctx, 0, 1)
    with open("{0}-think.txt".format(ctx.guild.id)) as phraselist:
        phrases = [line for line in phraselist.readlines()]
    await ctx.send(emoji.emojize(random.choice(phrases).format(ctx.author.mention)))
    await ctx.message.delete()

@bot.command()
async def shutup(ctx):
    if await admin(ctx):
        setting(ctx.guild.id).talk = False
        changesetting(ctx, 0, 0)
        await ctx.send("Okay... :(")
    else:
        await ctx.send("No >:(")

@bot.command()
@commands.check(admin)
async def prefix(ctx, newprefix):
    if len(newprefix) == 1 and newprefix in ":;~-+=.,!$&^?":
        setting(ctx.guild.id).prefix = newprefix
        changesetting(ctx, 1, newprefix)
        await ctx.send("Prefix set to: {0}".format(newprefix))
    else:
        await ctx.send("Invalid prefix! Avaliable prefixes: `:;~-+=.,!$&^?`")

@bot.command()
@commands.check(owner)
async def adminset(ctx, role):
    if role == "?":
        await ctx.send("Admin role is: "+ctx.guild.get_role(setting(ctx.guild.id).adminrole).mention)
        return
    try:
        role = int(role.strip("<@&>"))
    except ValueError:
        await ctx.send("Please give a valid role!")
        return
    if ctx.guild.get_role(role) == None:
        await ctx.send("This role does not exist!")
        return
    setting(ctx.guild.id).adminrole = role
    changesetting(ctx, 2, role)
    await ctx.send("Admin role set to: {0}".format(ctx.guild.get_role(role).mention))

@bot.command()
@commands.check(admin) 
async def freq(ctx, freq):
    if freq == "?":
        await ctx.send("Frequency: 1/{0}".format(setting(ctx.guild.id).freq))
        return
    try:
        freq = int(freq)
    except ValueError:
        await ctx.send("Please input an integer!")
        return
    if freq > 0:
        setting(ctx.guild.id).freq = freq
        changesetting(ctx, 3, freq)
        await ctx.send("Frequency set to 1/{0}!".format(freq))
    else:
        await ctx.send("Please input a number higher than `0`!")

@bot.command()
@commands.check(admin) 
async def whitelist(ctx, flag, *args):
    if flag == "l":
        await ctx.send("Whitelisted channels: "+str(" ".join([ctx.guild.get_channel(textchannel).mention for textchannel in setting(ctx.guild.id).whitelisted])))
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
        elif channel in setting(ctx.guild.id).whitelisted:
            await ctx.send("This channel is already whitelisted!")
        else:
            setting(ctx.guild.id).whitelisted.append(channel)
            changesetting(ctx, 4, setting(ctx.guild.id).whitelisted)
            await ctx.send("Added channel to whitelist!")
    elif flag == "rm":
        try:
            setting(ctx.guild.id).whitelisted.remove(channel)
        except ValueError:
            await ctx.send("Could not find that in the whitelist!")
            return
        changesetting(ctx, 4, setting(ctx.guild.id).whitelisted)
        await ctx.send("Channel removed!")
    else:
        await ctx.send("Unknown flag! Flags are: `a, rm, l`")

@bot.command()
@commands.check(admin) 
async def log(ctx, flag, *args):
    if flag == "n":
        setting(ctx.guild.id).log = False
        changesetting(ctx, 5, 0)
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
        elif channel in setting(ctx.guild.id).whitelisted:
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
            setting(ctx.guild.id).log = True
            setting(ctx.guild.id).lchannel = channel
            changesetting(ctx, 5, "1")
            changesetting(ctx, 6, channel)
            await ctx.send("Logging channel set!")
            await ctx.guild.get_channel(channel).send("```Logs will now appear in this channel. Happy monitoring!```")
    else:
        await ctx.send("Unknown flag! Flags are: `y, n`")

@bot.command()
@commands.check(admin) 
async def list(ctx, flag, *args):
    with open("{0}-think.txt".format(ctx.guild.id)) as phraselist:
        phrases = [line for line in phraselist.readlines()]
    if flag == "l":
        phrasestemp = []
        for index, phrase in enumerate(phrases):
            phrasestemp.append("{0}: ".format(index)+phrase)
            if index != 0: #seperates it into chunks of 30, so that it doesn't meet the 2000 char limit on discord.
                if index % 30 == 0:
                    await ctx.send("```"+"".join(phrasestemp)+"```")
                    phrasestemp = []
        if len(phrasestemp) != 0:
            await ctx.send("```"+"".join(phrasestemp)+"```") #sends the remainder
        return
    
    elif flag == "rm":
        try:
            index = int(args[0])
        except ValueError:
            await ctx.send("Please input an integer!")
            return
        try:
            phrase = phrases[index] #instead of saying deleted first, it will delete first, then if it fails, it will show an error.
            phrases.pop(index)
            await ctx.send("Deleted phrase: "+phrase)
        except IndexError:
            await ctx.send("Cannot find that in the list!")
            return
        
    elif flag == "a":
        phrases.append(args[0]+"\n")
        while len(phrases) > setting(ctx.guild.id).listmax:
            phrases.pop(0)
        await ctx.send("Added phrase!")
        
    elif flag == "max":
        if args[0] == "?":
            await ctx.send("List maximum is: `"+str(setting(ctx.guild.id).listmax)+"`")
            return
        try:
            maximum = int(args[0])
        except ValueError:
            await ctx.send("Please input an integer!")
            return
        if maximum > 4:
            setting(ctx.guild.id).listmax = maximum
            changesetting(ctx, 7, maximum)
            await ctx.send("List maximum set to: `"+str(maximum)+"`")
        else:
            await ctx.send("Please input a number higher than `4`")
            
    else:
        await ctx.send("Unknown flag! Flags are: `l, a, rm, max`")
    with open("{0}-think.txt".format(ctx.guild.id), "w") as phraselist:
        phraselist.writelines(phrases)
        
bot.run("") #insert the bot token there as str
