import os

from dotenv import load_dotenv

from citydao.bot import TelegramBot


def main() -> None:
    load_dotenv()

    telegram_bot = TelegramBot(
        token=os.getenv("TELEGRAM_TOKEN"),
        chat_id=os.getenv("TELEGRAM_CHAT_ID"),
    )
    telegram_bot.init_twitter(
        apikey=os.getenv("TWITTER_APIKEY"),
        api_secret=os.getenv("TWITTER_API_SECRET"),
    )
    proposal_msg = telegram_bot.get_proposals_msg()
    tweets_msg = telegram_bot.get_tweets_msg()
    treasury_msg = telegram_bot.get_treasury_msg()

    # send telegram message
    telegram_bot.send_message(
        msg=tweets_msg
    )

    telegram_bot.send_message(
        msg=treasury_msg
    )

    telegram_bot.send_message(
        msg=proposal_msg
    )

if __name__ == "__main__":
    main()
