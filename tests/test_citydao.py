import os
import sys
import unittest
from datetime import datetime, timedelta

from dotenv import load_dotenv

sys.path.append("/home/chompk/Works/cdao/citydao")

from citydao.calendar import CityDAOCalendar
from citydao.spotify import CityDAOSpotify
from citydao.treasury import CityDAOTreasury
from citydao.tweets import CityDAOTwitter


class CityDAOTester(unittest.TestCase):

    def setUp(self):
        load_dotenv()


    def test_isin_today(self):
        ytd = datetime.now() - timedelta(days=1)
        assert CityDAOTwitter._is_date_in_ytd(ytd)
        assert not CityDAOTwitter._is_date_in_ytd(ytd - timedelta(days=2))


    def test_fetch_twitter(self):
        citydao_twitter = CityDAOTwitter(
            apikey=os.getenv("TWITTER_APIKEY"),
            api_secret=os.getenv("TWITTER_API_SECRET")
        )
        latest_tweets = citydao_twitter.fetch_recent_tweets()
        today_tweets = citydao_twitter.filter_today_tweets(latest_tweets)


    def test_balance(self):
        treasury = CityDAOTreasury()
        balance = treasury.get_balance()


    def test_calendar(self):
        calendar = CityDAOCalendar(os.getenv("GOOGLE_APIKEY"))
        events = calendar.get_today_events()


    def test_spotify(self):
        spotify = CityDAOSpotify(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_credentials=os.getenv("SPOTIFY_CLIENT_CREDENTIALS")
        )
        episodes = spotify.get_latest_episodes()


if __name__ == "__main__":
    CityDAOTester().test_spotify()
    # unittest.main()
