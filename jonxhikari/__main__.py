import uvloop

from jonxhikari import __version__
from jonxhikari import Bot


def main() -> None:
    uvloop.install()
    bot = Bot(__version__)
    bot.run()


if __name__ == "__main__":
    main()
