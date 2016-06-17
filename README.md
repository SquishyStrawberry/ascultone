# Ascultone

Ascultone is an IRC bot, built to be easily extendable through its API.

What does the name mean?
------------------------

Ascultone is the name of a dragon in Sardinian culture;

You can read more about him in this
 [Wikipedia article](https://en.wikipedia.org/w/index.php?title=Scultone&action=edit&redlink=1).

How to setup
------------

1. Make sure Python 3.5 is installed, you can get it from
   [python.org](http://python.org/).
2. Install the required dependencies, using `requirements.txt`. In Linux, you
   just need to type `python3 -m pip install -r requirements.txt`
3. Copy `config.sample.yaml` to `config.yaml` and edit it to your heart's
   desire.
4. You're now done with setup, you can just run it with `python3 -m ascultone`.

The API
-------

### How to add a plugin

In the YAML configuration file, under the key `modules`, you need to add the
path to your plugin filename, relative to the bot's directory.

### How to write a plugin

Once a module is loaded, the bot calls the function `init_module`, where you
will have to initialize all your callbacks with function such as
`register_command` or `register_trigger`.

## Goals

* Full RFC 2812 compliance
* Maybe IRCv3?

