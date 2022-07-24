import os
from datetime import datetime, timedelta

import pytest
from dotenv import load_dotenv
from citydao.calendar import CityDAOCalendar

from citydao.treasury import CityDAOTreasury
from citydao.tweets import CityDAOTwitter


@pytest.fixture(scope="session", autouse=True)
def execute_before_any_test():
    load_dotenv()


def test_isin_today():
    ytd = datetime.now() - timedelta(days=1)
    assert CityDAOTwitter._is_date_in_ytd(ytd)
    assert not CityDAOTwitter._is_date_in_ytd(ytd - timedelta(days=2))


def test_fetch_twitter():
    citydao_twitter = CityDAOTwitter(
        apikey=os.getenv("TWITTER_APIKEY"),
        api_secret=os.getenv("TWITTER_API_SECRET")
    )
    latest_tweets = citydao_twitter.fetch_recent_tweets()
    today_tweets = citydao_twitter.filter_today_tweets(latest_tweets)


def test_balance():
    treasury = CityDAOTreasury()
    balance = treasury.get_balance()


def test_calendar():
    calendar = CityDAOCalendar(os.getenv("GOOGLE_APIKEY"))
    events = calendar.get_today_events()

    assert True


if __name__ == "__main__":
    test_calendar()
