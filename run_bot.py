import os
from dotenv import load_dotenv

from citydao.bot import TelegramBot


def main():
    load_dotenv()

    bot = TelegramBot(token=os.getenv("TELEGRAM_TOKEN", None))
    bot.run()


if __name__ == "__main__":
    main()
