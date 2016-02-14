# Ascultone

Ascultone is an IRC bot, built to be easily extendable through its API

## What does the name mean?

Ascultone is the name of a dragon in Sardinian culture;
You can read more about him in this
 [Wikipedia article](https://en.wikipedia.org/w/index.php?title=Scultone&action=edit&redlink=1)
A dragon was chosen to keep the theme of dragon-themed bots in my favorite IRC
channel.

## The API

### How to add a plugin

In the YAML configuration file, under the key `modules`, you need to add the
path to your plugin filename, relative to the bot's directory

### How to write a plugin

Once a module is loaded, the bot calls the function `init_module`, where you
will have to initialize all your callbacks with function such as
`register_command` or `register_trigger`.

## Goals

* Full RFC 2812 compliance
* Maybe IRCv3?

