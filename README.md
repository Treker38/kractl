Starts commands with the prefix, or ping the bot first. Using prefix after pinging the bot does not work. (Create an issue if this is annoying)

## Normal commands:
* hi            - get greeted by the bot
* hug           - hug the bot
* lamp          - shows you moths around a lamp
* moth          - shows you a moth
* help          - brings you to this readme file

## Admin commands:
* speak         - enables random speaking
* shutup        - disables random speaking, still listens
* prefix        - sets prefix, avaliable prefixes: :;~-+=.,!$&^?                            = `prefix <flag>`
* freq          - sets the frequency of which the bot sends a message                       = `freq <number>`
* talkchannel   - recommended for #general, sets the channel which the bot randomly speaks. = `talkchannel <flag> <channel>` flags: a, rm, ? - if using ?, channel is not taken.
* log           - not recommended at all to use, logs what it learns in any channel.        = `log <flag> <channel>` flags: y, n - if using n, channel is not taken.

## Owner-only commands:
* adminset      - sets what role will be able to use the admin commands for the bot         = `adminset <role>` 

## Additional info:
talkchannel flags are `a, rm, ?` `a` = add, `rm` = remove, `?` = what are the channels whitelisted.

Example: `-talkchannel a #general` Will add #general to the whitelisted channels. You can add as many as you like but the bot will only randomly speak in the whitelisted channels, to check what channels are whitelisted, you can do: `-talkchannel ?`

Setting a role, with adminset will allow other roles which are higher in rank than the adminrole to use admin commands.
