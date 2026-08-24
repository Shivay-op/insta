from . import start, join, broadcast, link


def setup_handlers(bot):
    start.register(bot)
    join.register(bot)
    broadcast.register(bot)
    link.register(bot)
