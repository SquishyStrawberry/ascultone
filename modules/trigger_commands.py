#!/usr/bin/env python3
import re

GROUP_REGEXP = re.compile(
    r"\$\{(.*?)\}"
)

# TODO Maybe refactor this into a class..?
compiled_triggers = {}


def init_module(bot):
    global compiled_triggers

    bot.cursor.execute(
        "CREATE TABLE IF NOT EXISTS Triggers "
        "(id INTEGER PRIMARY KEY AUTOINCREMENT,"
        " trigger TEXT NOT NULL,"
        " response TEXT NOT NULL)"
    )
    bot.register_command("learn", add_trigger)
    bot.register_command("forget", remove_trigger)
    bot.register_privmsg(trigger_dispatcher)
    # FIXME Learn previously stored commands
    bot.cursor.execute(
        "SELECT trigger, response "
        "FROM Triggers"
    )
    for trigger, response in bot.cursor.fetchall():
        compiled_triggers[re.compile(trigger)] = response


def add_trigger(event):
    if not event.bot.has_flag(event.sender, "whitelisted"):
        return
    trigger, response = event.param_text.split(" -> ")
    compiled_trigger = re.compile(trigger)
    compiled_triggers[compiled_trigger] = response
    event.bot.cursor.execute(
        "INSERT INTO Triggers(trigger, response) "
        "VALUES (?, ?)", (trigger, response)
    )


def remove_trigger(event):
    if not event.bot.has_flag(event.sender, "whitelisted"):
        return
    trigger = event.param_text
    compiled_trigger = re.compile(trigger)
    del compiled_triggers[compiled_trigger]
    event.bot.cursor.execute(
        "DELETE FROM Triggers "
        "WHERE trigger=?", (trigger,)
    )


def trigger_dispatcher(event):
    for trigger, response in compiled_triggers.items():
        trigger_match = trigger.search(event.text)
        if trigger_match is not None:
            groups = {
                "nick": event.bot.nickname,
                "sender": event.sender.nickname
            }
            groups.update(trigger_match.groupdict())
            for match in GROUP_REGEXP.finditer(response):
                try:
                    response = response.replace(match.group(0),
                                                groups[match.group(1)])
                except KeyError:
                    # If the group is missing, leave the ${group}
                    continue
            event.bot.send_action(event.source, response)
