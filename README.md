Starts commands with the prefix, or ping the bot first. Using prefix after pinging the bot does not work. (Create an issue if this is annoying)

## Normal commands:
* hi            - get greeted by the bot
* hug           - hug the bot
* lamp          - shows you moths around a lamp
* moth          - shows you a moth
* proper        - sends a proper message back
* help          - brings you to this readme file

## Admin commands:
* speak         - enables random speaking
* shutup        - disables random speaking, still listens
* prefix        - sets prefix, avaliable prefixes: :;~-+=.,!$&^?                            = `prefix <prefix>`
* freq          - sets the frequency of which the bot sends a message                       = `freq <number>` using `?` instead of a number will show you you the frequency
* whitelist   - recommended for #general, sets the channel which the bot randomly speaks.   = `whitelist <flag> <channel>` flags: `a, rm, ?` - if using ?, channel is not taken.
* log           - not recommended at all to use, logs what it learns in any channel.        = `log <flag> <channel>` flags: `y, n` - if using `n`, `<channel>` is not taken.
* list          - manages the list of phrases                                               = `list <flag> <item>` flags: `l, a, rm, max` `l` lists the phrases, `a "<string>"` adds whatever you want to the list of phrases **use quotes!!!** see additional info, `rm <index>` removes a phrase, given the index. use `l` to get the index number. `max <flag>` sets the maximum amount of phrases at one time. flags are: `?` will show you the maximum.

## Owner-only commands:
* adminset      - sets what role will be able to use the admin commands for the bot         = `adminset <role>` using `?` instead of a role will show you the current admin role

## Additional info:
`-talkchannel a #general` Will add #general to the whitelisted channels. You can add as many as you like but the bot will only randomly speak in the whitelisted channels, to check what channels are whitelisted, you can do: `-talkchannel ?`

Setting a role, with adminset will allow other roles which are higher in rank than the adminrole to use admin commands.

Why does `list a my phrase here` only come out as `my`?
* It's a limitation, sadly. You will have to do `list a "my phrase here"` and it will come out as `my phrase here` this might be fixed later on, but definetly not soon.
