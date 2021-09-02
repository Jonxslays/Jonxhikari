import uvloop

from jonxhikari import __version__
from jonxhikari import Bot


def main() -> None:
    uvloop.install()
    bot = Bot(__version__)

    try:
        bot.run()
    except KeyboardInterrupt:
        print("Exiting...")
        bot.close()


if __name__ == "__main__":
    main()
