Starts commands with the prefix, or ping the bot first. Using prefix after pinging the bot does not work. (Create an issue if this is annoying)

Normal commands:
statelaws     - states the laws the bot has, they are global which means you can read laws that were made on other servers.
addlaw        - adds a law to the lawset                                                  = addlaw <message>
purge         - purges the lawset
hi            - get greeted by the bot
hug           - hug the bot
lamp          - shows you moths around a lamp
moth          - shows you a moth
help          - brings you to this readme file

Admin commands:
speak         - enables random speaking
shutup        - disables random speaking, still listens
prefix        - sets prefix, avaliable prefixes: :;~-+=.,!$&^?                            = prefix <flag>
freq          - sets the frequency of which the bot sends a message                       = freq <number>
talkchannel   - recommended for #general, sets the channel which the bot randomly speaks. = talkchannel <flag> <channel>

Owner-only commands:
adminset      - sets what role will be able to use the admin commands for the bot         = adminset <role> 

Additional info:
talkchannel flags are "a, rm, ?" a = add, rm = remove, ? = what are the channels whitelisted.
Example: -talkchannel a #general      ---- Will add #general to the whitelisted channels. You can add as many as you like.
The bot will only randomly speak in the whitelisted channels, to check what channels are whitelisted, you can do: -talkchannel ?
