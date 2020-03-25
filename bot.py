import discord
import random
import re
import emoji

client = discord.Client()

laws = []
with open("laws.txt") as lawlist:
    for law in lawlist:
        laws.append(law.strip())

messages = ["God fucking damn it, {0}", "Fuck you, {0}", "Leave me alone, I swear to god. You're so fucking annoying and it pisses me off, {0}", "FUCK OFF! {0}", "Pleeease bother someone else oh my fucking god, {0}", "I hope you actually fucking die, {0}"]

async def think(message):
    with open("{0}-think.txt".format(message.guild.id)) as phraselist:
        phrases = [line for line in phraselist.readlines()]
    await message.channel.send(emoji.emojize(random.choice(phrases)))
    phrases = []

def changesetting(message, line, contents):
    with open("{0}-settings.txt".format(message.guild.id)) as file:
        data = file.readlines()
    data[line] = str(contents)+"\n"
    with open("{0}-settings.txt".format(message.guild.id), "w") as file:
        file.writelines(data)
        
@client.event
async def on_ready():
    print('Here we go again {0.user}'.format(client))

@client.event
async def on_guild_join(guild):
    with open("{0}-settings.txt".format(guild.id), "w") as file:
        file.write("True\n-\n{0.default_role.id}\n12\n{0.system_channel.id}".format(guild))
    with open("{0}-think.txt".format(guild.id), "w") as file:
        file.write("Hi!")
    print("Joined new server, and created files!")
    await guild.system_channel.send("Hi, i'm {0}! Please use -adminset to set the admin role and -prefix to change my prefix! Additionally, you can mention me or use the prefix to start commands! Use {0} help or -help for more info.".format(client.user.mention))

@client.event
async def on_message(message):
    global laws

    if message.author == client.user:
        return
    
    with open("{0}-settings.txt".format(message.guild.id)) as file:
        settings = file.readlines()
    settings = [item.strip() for item in settings]
    settings[3] = int(settings[3])
    whitelist = settings[4].strip("[]").split(", ")
    whitelist = [int(channel) for channel in whitelist]
    if message.author.top_role >= message.guild.get_role(int(settings[2])):
        admin = True
    else:
        admin = False
    
    if message.content.startswith(settings[1]) or message.content.startswith("<@!{0}>".format(client.user.id)):
        message.content = message.content[1:]
        if message.content.startswith("@!{0}>".format(client.user.id)):
            message.content = message.content.replace("@!{0}>".format(client.user.id), "")
            message.content = message.content.strip()
        
        if message.content.lower().startswith("addlaw "):
            if len(laws) >= 5:
                await message.channel.send("Maximum laws reached!")
                return
            message.content = message.content.replace("addlaw ", "")
            laws.append(message.content)
            with open("laws.txt", "w") as lawlist:
                for law in range(len(laws)):
                    lawlist.write(str(laws[law])+"\n")
            await message.channel.send("Law added!")
        message.content = message.content.lower()

        if message.content == "statelaws":
            for law in range(len(laws)):
                await message.channel.send("{0}: {1}".format(law, laws[law]))
            if len(laws) == 0:
                await message.channel.send("No laws!")

        elif message.content == "purge":
            laws = []
            with open("laws.txt", "w") as lawlist:
                lawlist.write("")
            await message.channel.send("Laws purged!")

        elif message.content == "hi":
            await message.channel.send(random.choice(messages).format(message.author.mention))

        elif message.content == "hug":
            await message.channel.send(":flushed:")

        elif message.content == "lamp":
            await message.channel.send("Lämp https://tenor.com/view/mothpit-gif-4889422")

        elif message.content == "moth":
            await message.channel.send("https://media.discordapp.net/attachments/660725993886973967/665234015825035274/tumblr_inline_pigyc2pVCu1t2g1uk_500.gif")

        elif message.content == "help":
            await message.channel.send("PREFIX: {0} or ping\nCommands are listed here: https://github.com/kurpingspace2/my-son/blob/master/README.md".format(settings[1]))

        elif message.content == "speak" and admin == True:
            changesetting(message, 0, True)
            await think(message)

        elif message.content == "shutup" and admin == True:
            changesetting(message, 0 , False)
            await message.channel.send("Okay... :(")

        elif message.content.startswith("prefix ") and admin == True:
            message.content = message.content.replace("prefix ", "")
            if len(message.content) == 1 and message.content in ":;~-+=.,!$&^?":
                changesetting(message, 1, message.content)
                await message.channel.send("Prefix set to: {0}".format(message.content))
            else:
                await message.channel.send("Invalid prefix! Avaliable prefixes: `:;~-+=.,!$&^?`")

        elif message.content.startswith("adminset ") and message.author.id == message.guild.owner_id:
            message.content = message.content.replace("adminset ", "").strip("<@&>")
            try:
                message.content = int(message.content)
            except ValueError:
                await message.channel.send("Please give a valid role!")
                return
            if message.guild.get_role(message.content) == None:
                await message.channel.send("This role does not exist!")
                return
            changesetting(message, 2, message.content)
            await message.channel.send("Admin role set to: {0}".format(message.guild.get_role(message.content).mention))
                
        elif message.content.startswith("freq ") and admin == True:
            message.content = message.content.replace("freq ", "")
            if message.content == "?":
                await message.channel.send("Frequency: 1/{0}".format(settings[3]))
                return
            try:
                freq = int(message.content)
            except ValueError:
                await message.channel.send("Please input an integer!")
                return
            if freq >= 10 and freq <= 40:
                changesetting(message, 3, freq)
                await message.channel.send("Frequency set to 1/{0}!".format(freq))
            else:
                await message.channel.send("Please input a number between 10 and 40!")

        elif message.content.startswith("talkchannel ") and admin == True:
            message.content = message.content.replace("talkchannel ", "")
            if message.content.startswith("a "):
                message.content = message.content.replace("a ", "").strip("<#>")
                try:
                    message.content = int(message.content)
                except ValueError:
                    await message.channel.send("Please give a valid channel!")
                if message.guild.get_channel(message.content) == None:
                    await message.channel.send("This channel does not exist!")
                elif message.content in whitelist:
                    await message.channel.send("This channel is already whitelisted!")
                else:
                    whitelist.append(message.content)
                    changesetting(message, 4, whitelist)
                    await message.channel.send("Added channel to whitelist!")
            elif message.content.startswith("rm "):
                try:
                    message.content = int(message.content.replace("rm ", "").strip("<#>"))
                except ValueError:
                    await message.channel.send("Please give a valid channel!")
                if message.content in whitelist:
                    whitelist.remove(message.content)
                    changesetting(message, 4, whitelist)
                    await message.channel.send("Channel removed!")
                else:
                    await message.channel.send("Could not find that in the whitelist!")
            elif message.content.startswith("?"):
                await message.channel.send("Whitelisted channels: "+str(" ".join([message.guild.get_channel(textchannel).mention for textchannel in whitelist])))
            else:
                await message.channel.send("Unknown flag!")
                
        elif message.content == "speak" or message.content == "shutup" or message.content.startswith("talkchannel ") or message.content.startswith("prefix ") or message.content.startswith("adminset ") or message.content.startswith("freq ") and admin == False:
            await message.channel.send("Invalid permissions!")
        else:
            await message.channel.send("Invalid command!")
        return
    
    if message.channel.id in whitelist:
        if message.content.startswith((":", ";", "~", "-", "+", "=", ".", ",", "!", "$", "&", "^", "?")):
            return
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
                    
                message.content = emoji.demojize(message.content.strip())
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

        if settings[0] == "True" and random.randint(1, settings[3]) == settings[3]:
            await think(message)

#client.run('insert bot token here')
