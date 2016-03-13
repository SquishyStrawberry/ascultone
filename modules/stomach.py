#!/usr/bin/env python3


def init_module(bot):
    bot.cursor.execute(
        "CREATE TABLE IF NOT EXISTS "
        "Stomach "
        "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "content TEXT NOT NULL)"
    )
    bot.register_command("stomach", display_stomach)
    bot.register_command("eat", eat_something)
    bot.register_command("spit", spit_something)
    bot.register_command("vomit", vomit_stomach)


def display_stomach(self, source, sender, params):
    module_config = self.config["module_config"]["stomach"]
    victims = ""
    self.cursor.execute(
        "SELECT content "
        "FROM Stomach"
    )
    stomach = self.cursor.fetchall()
    if len(stomach) == 0:
        victims = "nothing"
    elif len(stomach) == 1:
        victims = "just {}".format(stomach[0])
    else:
        victims = "{}, and {}".format(", ".join(victims[:-1]), victims[-1])
    self.send_action(source,
                      module_config["stomach_message"].format(victims=victims))


def eat_something(self, source, sender, params):
    pass


def spit_something(self, source, sender, params):
    pass


def vomit_stomach(self, source, sender, params):
    pass
