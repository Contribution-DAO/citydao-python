from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
import pytz

import tweepy as tw


@dataclass
class Tweet(object):
    id: str
    text: str
    created_at: datetime
    fav_count: Optional[int] = None
    rtw_count: Optional[int] = None

    def __post_init__(self) -> None:
        self.url = f"https://twitter.com/citydao/status/{self.id}"

    def __repr__(self) -> str:
        return f"Tweet({self.url})"


class CityDAOTwitter(object):

    def __init__(self, apikey: str, api_secret: str) -> None:
        auth = tw.OAuth1UserHandler(apikey, api_secret)
        self.api = tw.API(auth, wait_on_rate_limit=True)
        self.account = "CityDAO"

    def fetch_recent_tweets(self) -> List[str]:
        tweets = self.api.user_timeline(
            screen_name=self.account, 
            include_rts=False,
            exclude_replies=True,
            count=200
        )
        return [
            Tweet(
                id=tweet.id,
                text=tweet.text,
                created_at=tweet.created_at,
                fav_count=tweet.favorite_count,
                rtw_count=tweet.retweet_count
            )
            for tweet in tweets
        ]

    @staticmethod
    def _is_date_in_ytd(date: datetime) -> bool:
        end_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0).replace(tzinfo=pytz.UTC)
        start_date = end_date - timedelta(days=1)
        
        date = date.replace(tzinfo=pytz.UTC)
        is_in_ytd = date > start_date and date <= end_date
        return is_in_ytd
        
        
    def filter_today_tweets(self, tweets: List[Tweet], return_others: bool = False) -> List[str]:
        today_tweets = []
        others = []
        for tweet in tweets:
            if CityDAOTwitter._is_date_in_ytd(tweet.created_at):
                today_tweets.append(tweet)
            else:
                others.append(tweet)
    
        if return_others:
            return today_tweets, others
        
        return today_tweets

    def format_tweets(self, new_tweets: List[Tweet], other_tweets: List[Tweet]) -> str:
        template = "🌆 Here's latest CityDAO tweets \\([@CityDAO](https://twitter.com/citydao)\\)\n\n"

        if len(new_tweets) == 0:
            template += f"🥱 There's no new tweets from [@CityDAO](https://twitter.com/citydao)\\!\n\n"
        else:
            template += f"🎏 There's {len(new_tweets)} Tweets\\!\n\n"

        for i, tweet in enumerate(new_tweets):
            template += f"👉 `{tweet.text[:100]}...`\n"
            template += f"   [Read full tweet here]({tweet.url})\n"
            template += f"   💚 {tweet.fav_count:03d}\t🔁 {tweet.rtw_count:03d}\n"
            template += f"   ⏰ Tweeted on: {tweet.created_at.strftime('%d %b %Y %H:%M:%S UTC')}\n\n"

        if len(other_tweets) > 0:
            template += f"Checkout other tweets from [@CityDAO](https://twitter.com/citydao)\\!\n\n"

            for i, tweet in enumerate(other_tweets):
                template += f"👉 `{tweet.text[:100]}...`\n"
                template += f"   [Read full tweet here]({tweet.url})\n"
                template += f"   💚 {tweet.fav_count:03d}\t🔁 {tweet.rtw_count:03d}\n"
                template += f"   ⏰ Tweeted on: {tweet.created_at.strftime('%d %b %Y %H:%M:%S UTC')}\n\n"


        template += "\n🟩 Have a great day Citizen\\! 🟩"
        return template

    def get_daily_summary(self, n_tweets: int = 3) -> str:
        latest_tweets = self.fetch_recent_tweets()
        new_tweets, other_tweets = self.filter_today_tweets(latest_tweets, return_others=True)
        other_tweets = other_tweets[:max(0, n_tweets - len(new_tweets))]

        # today tweets + other latest tweets with maximum of n

        return self.format_tweets(new_tweets, other_tweets)
