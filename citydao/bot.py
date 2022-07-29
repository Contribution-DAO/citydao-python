import logging
from typing import Optional

import telegram
from telegram.ext import CommandHandler, Updater
from telegram.parsemode import ParseMode

from citydao.calendar import CityDAOCalendar
from citydao.snapshot import SnapshotAPI
from citydao.spotify import CityDAOSpotify
from citydao.treasury import CityDAOTreasury
from citydao.tweets import CityDAOTwitter


class Bot(object):

    def __init__(self, **kwargs) -> None:
        self.snapshot = SnapshotAPI()
        self.citydao_twitter = None
        self.treasury = CityDAOTreasury()

    def init_spotify(self, client_id: str, client_credentials) -> None:
        self.citydao_spotify = CityDAOSpotify(client_id, client_credentials)

    def init_twitter(self, apikey: str, api_secret: str) -> None:
        self.citydao_twitter = CityDAOTwitter(apikey, api_secret)

    def init_google(self, apikey: str) -> None:
        self.calendar = CityDAOCalendar(apikey)

    def get_proposals_msg(self) -> str:
        return self.snapshot.get_daily_summary()

    def get_tweets_msg(self) -> str:
        return self.citydao_twitter.get_daily_summary()

    def get_treasury_msg(self) -> str:
        return self.treasury.get_daily_summary()

    def get_calendar_msg(self) -> str:
        return self.calendar.get_daily_summary()

    def get_spotify_msg(self) -> str:
        return self.citydao_spotify.get_daily_summary()

    def send_message(self, msg: str) -> None:
        raise NotImplementedError()

    def run(self) -> None:
        raise NotImplementedError


class TelegramBot(Bot):

    def __init__(self, token: str, chat_id: Optional[str] = None) -> None:
        super().__init__()
        self.bot = telegram.Bot(token=token)
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.chat_id = chat_id

    def set_chat_id(self, chat_id: str) -> None:
        self.chat_id = chat_id

    def send_message(self, msg: str, parse_mode: ParseMode = ParseMode.MARKDOWN_V2) -> None:
        if len(msg) == 0:
            return
        self.bot.send_message(
            chat_id=self.chat_id,
            text=msg,
            parse_mode=parse_mode
        )

    def proposal_handler(self) -> None:
        self.send_message(
            self.get_proposals_msg(),
        )
        self.bot.send_message()

    def run(self) -> None:
        logging.info("Starting telegram bot...")

        self.updater.dispatcher.add_handler(
            CommandHandler(
                "proposals",
                self.get_proposals_msg
            )
        )

        self.updater.dispatcher.add_handler(
            CommandHandler(
                "tweets",
                self.get_tweets_msg
            )
        )

        self.updater.dispatcher.add_handler(
            CommandHandler(
                "calendar",
                self.get_calendar_msg
            )
        )

        self.updater.dispatcher.add_handler(
            CommandHandler(
                "treasury",
                self.get_treasury_msg
            )
        )

        self.updater.dispatcher.add_handler(
            CommandHandler(
                "spotify",
                self.get_spotify_msg
            )
        )
