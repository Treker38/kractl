print("Inizializing!")

import discord
from discord.ext import commands
import random
import re
import emoji

messages = ["God fucking damn it, {0}", "Fuck you, {0}", "Leave me alone, I swear to god. You're so fucking annoying and it pisses me off, {0}", "FUCK OFF! {0}", "Pleeease bother someone else oh my fucking god, {0}", "I hope you actually fucking die, {0}"]
guilds = {}

def changesetting(ctx, line, contents):
    with open("{0}-settings.txt".format(ctx.guild.id)) as file:
        data = file.readlines()
    data[line] = str(contents)+"\n"
    with open("{0}-settings.txt".format(ctx.guild.id), "w") as file:
        file.writelines(data)

class Server:
    def __init__(self, t, p, a, f, w):
        self.talk = t
        self.prefix = p
        self.adminRole = a
        self.freq = f
        self.whitelisted = w

def setting(guildId):
    if guildId in guilds:
        return guilds[guildId]
    return None

async def determine_prefix(bot, msg):
    if msg.guild: #if message is in a guild
        return setting(msg.guild.id).prefix
    else:
        return "-"
    
bot = commands.Bot(command_prefix=determine_prefix)
bot.remove_command('help') #removes the prebuilt help command

@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None

async def admin(ctx):
    if ctx.author.top_role >= ctx.guild.get_role(setting(ctx.guild.id).adminRole):
        return True
    return False

async def owner(ctx):
    if ctx.author.id == ctx.guild.owner.id:
        return True
    return False

@bot.event
async def on_ready():
    with open("servers.txt") as servers:
        servers = [line.strip()+"-settings.txt" for line in servers.readlines()]
    for guild in servers:
        with open(guild) as settings:
            settings = settings.readlines()
        settings = [item.strip() for item in settings]
        guilds[int(guild.strip("-settings.txt"))] = Server(bool(int(settings[0])), settings[1], int(settings[2]), int(settings[3]), [int(setting) for setting in settings[4].strip("[]").split(", ")])
    print('Here we go again {0.user}'.format(bot))

@bot.event
async def on_guild_join(guild):
    with open("{0}-settings.txt".format(guild.id), "w") as file:
        file.write("1\n-\n{0.default_role.id}\n12\n{0.system_channel.id}".format(guild))
    with open("{0}-think.txt".format(guild.id), "w") as file:
        file.write("Hi!")
    with open("servers.txt", "a") as file:
        file.write("\n{0}".format(guild.id))
    await guild.system_channel.send("Hi, i'm {0}! Please use -adminset to set the admin role and -prefix to change my prefix! Additionally, you can mention me or use the prefix to start commands! Use {0} help or -help for more info.".format(bot.user.mention))
    guilds[guild.id] = Server(True, "-", guild.default_role.id, 12, [guild.system_channel.id])
    print("Joined new server, and created files!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith((":", ";", "~", "-", "+", "=", ".", ",", "!", "$", "&", "^", "?")): #ignores commands for every bot in a server, this isn't just brute-force
        await bot.process_commands(message)
        return #don't want it to continue after running a command
    if message.channel.id in setting(message.guild.id).whitelisted:
        if random.randint(1,10) == 10:
            with open("{0}-think.txt".format(message.guild.id)) as file:
                phrases = [line.strip() for line in file.readlines()]
                if "<@" in message.content:
                    message.content = re.sub("<[^>]+>", "", message.content)
                    
                if message.attachments != []:
                    message.content = message.content+" "+message.attachments[0].url
                    message.content = message.content.strip()
                    
                if message.content == "" or message.content == "** **" or message.content == "*** ***":
                    message.content = "_ _"
                    
                elif "\n" in message.content:
                    message.content = message.content.replace("\n", " ")
                    
                message.content = emoji.demojize(message.content.strip()) #can't write unicode characters for some reason, gotta convert
                if message.content in phrases:
                    print(message.content, " is already in phrases!")
                    return
                
                phrases.append(message.content)
                if len(phrases) >= 40:
                    while len(phrases) > 40:
                        phrases.pop(0)
                        
                with open("{0}-think.txt".format(message.guild.id), "w") as phraselist:
                    for phrase in phrases:
                        phraselist.write(phrase+"\n")

            phrases = []
            print("New phrase added!", message.content)
        if setting(message.guild.id).talk and random.randint(1, setting(message.guild.id).freq) == setting(message.guild.id).freq:
            with open("{0}-think.txt".format(message.guild.id)) as phraselist:
                phrases = [line for line in phraselist.readlines()]
            await message.channel.send(emoji.emojize(random.choice(phrases))) #turns any emoji back into a unicode character and sends the message

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
    await ctx.send("PREFIX: {0} or ping\nCommands are listed here: https://github.com/kurpingspace2/my-son/blob/master/README.md".format(setting(ctx.guild.id).prefix))

@bot.command()
@commands.check(admin)
async def speak(ctx):
    setting(ctx.guild.id).talk = True
    changesetting(ctx, 0, 1)
    with open("{0}-think.txt".format(ctx.guild.id)) as phraselist:
        phrases = [line for line in phraselist.readlines()]
    await ctx.send(emoji.emojize(random.choice(phrases)))

@bot.command()
@commands.check(admin)
async def shutup(ctx):
    setting(ctx.guild.id).talk = False
    changesetting(ctx, 0, 0)
    await ctx.send("Okay... :(")

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
    try:
        role = int(role.strip("<@&>"))
    except ValueError:
        await ctx.send("Please give a valid role!")
        return
    if ctx.guild.get_role(role) == None:
        await ctx.send("This role does not exist!")
        return
    setting(ctx.guild.id).adminRole = role
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
    if freq >= 10 and freq <= 40:
        setting(ctx.guild.id).freq = freq
        changesetting(ctx, 3, freq)
        await ctx.send("Frequency set to 1/{0}!".format(freq))
    else:
        await ctx.send("Please input a number between 10 and 40!")

@bot.command()
@commands.check(admin) 
async def talkchannel(ctx, *args):
    try:
        flag = args[0]
    except IndexError:
        await ctx.send("Please insert a flag after command! Flags are: a, rm, ?")
        return
    if flag == "?":
        await ctx.send("Whitelisted channels: "+str(" ".join([ctx.guild.get_channel(textchannel).mention for textchannel in setting(ctx.guild.id).whitelisted])))
        return
    try:
        channel = args[1].strip("<#>")
        channel = int(channel)
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
        await ctx.send("Unknown flag! Flags are: a, rm, ?")

bot.run("") #insert the bot token there
