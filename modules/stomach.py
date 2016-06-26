#!/usr/bin/env python3


def init_module(bot):
    bot.cursor.execute(
        "CREATE TABLE IF NOT EXISTS Stomach "
        "(id INTEGER PRIMARY KEY AUTOINCREMENT, victim TEXT NOT NULL)"
    )
    bot.register_command("eat",     command_eat)
    bot.register_command("spit",    command_spit)
    bot.register_command("vomit",   command_vomit)
    bot.register_command("stomach", command_stomach)


def command_eat(event):
    messages = event.bot.config["modules"]["messages"]["stomach"]
    victim = event.param_text

    event.bot.cursor.execute(
        "INSERT INTO Stomach(victim) "
        "VALUES (?)", (victim,)
    )
    event.bot.send_action(event.source,
                          messages["eat"].format(victim=victim))


def command_spit(event):
    messages = event.bot.config["modules"]["messages"]["stomach"]
    victim = event.param_text
    event.bot.cursor.execute(
        "SELECT victim FROM Stomach "
        "WHERE lower(victim) = lower(?)", (victim,)
    )
    if event.bot.cursor.fetchone() is None:
        event.bot.send_action(event.source,
                              messages["spit_superfluous"].format(victim=victim))
    else:
        event.bot.send_action(event.source,
                              messages["spit"].format(victim=victim))
        event.bot.cursor.execute(
            "DELETE FROM Stomach "
            "WHERE lower(victim) = lower(?)", (victim,)
        )


def command_vomit(event):
    messages = event.bot.config["modules"]["messages"]["stomach"]

    event.bot.cursor.execute(
        "SELECT victim FROM Stomach"
    )
    if event.bot.cursor.fetchone() is None:
        event.bot.send_action(event.source, messages["vomit_superfluous"])
    else:
        event.bot.send_action(event.source, messages["vomit"])
        event.bot.cursor.execute(
            "DELETE FROM Stomach"
        )


def command_stomach(event):
    event.bot.cursor.execute(
        "SELECT victim FROM Stomach"
    )
    victims = list({i[0] for i in event.bot.cursor.fetchall()})
    message = event.bot.config["modules"]["messages"]["stomach"]["stomach"]
    if not victims:
        items = "nothing"
    elif len(victims) == 1:
        items = "just {}".format(victims[0])
    else:
        items = "{}, and {}".format(", ".join(victims[:-1]), victims[-1])
    event.bot.send_action(event.source, message.format(victims=items))
