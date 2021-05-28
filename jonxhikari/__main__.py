import hikari

from jonxhikari import __version__
from jonxhikari.bot import Bot


def main():
    bot = Bot(__version__)
    bot.run()


if __name__ == "__main__":
    main()
