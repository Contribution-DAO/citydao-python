import base64
from dataclasses import dataclass
from datetime import datetime, timedelta
import functools
from typing import List
import pytz

import requests


@dataclass
class SpotifyEpisode(object):
    name: str
    url: str
    created_at: datetime
    preview_url: str
    description: str
    duration: float

    def __post_init__(self):
        self.duration = SpotifyEpisode.sec_to_str(self.duration)

    def __repr__(self) -> str:
        return f"SpotifyEpisode(url={self.url})"

    @staticmethod
    def sec_to_str(duration_sec: float) -> str:
        minutes, seconds = divmod(duration_sec, 60)
        hours, minutes = divmod(minutes, 60)

        if hours == 0.:
            return f"{int(minutes)} minutes {seconds:.2f} seconds".replace(".", "\\.")
        else:
            return f"{int(hours)} hours {int(minutes)} minutes {seconds:.2f} seconds".replace(".", "\\.")


class CityDAOSpotify(object):

    def __init__(self, client_id: str, client_credentials: str) -> None:
        self.client_credentials = base64.urlsafe_b64encode(
            f"{client_id}:{client_credentials}".encode()
        ).decode()
        self.citydao_id = "4DqYWZyAMxUAL5o22caPSd"
        self.base_url = f"https://api.spotify.com"

    def issue_oauth(self) -> None:
        r = requests.post(
            f"https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {self.client_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "client_credentials",
            }
        )
        response = r.json()
        access_token = response.get("access_token")
        self.headers = {"Authorization": f"Bearer {access_token}"}

    def get_latest_episodes(self) -> List[SpotifyEpisode]:
        self.issue_oauth()
        endpoint = f"{self.base_url}/v1/shows/{self.citydao_id}/episodes?market=ES&limit=30"
        r = requests.get(
            endpoint,
            headers={ **self.headers }
        )
        response = r.json()
        episodes = [
            SpotifyEpisode(
                name=item["name"],
                url=item["external_urls"]["spotify"],
                created_at=datetime.strptime(item["release_date"], "%Y-%m-%d"),
                preview_url=item["audio_preview_url"],
                description=item["description"],
                duration=item["duration_ms"] / 1000
            )
            for item in response["items"]
        ]
        return episodes

    @staticmethod
    def _is_date_in_ytd(date: datetime) -> bool:
        end_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0).replace(tzinfo=pytz.UTC)
        start_date = end_date - timedelta(days=1)
        
        date = date.replace(tzinfo=pytz.UTC)
        is_in_ytd = date > start_date and date <= end_date
        return is_in_ytd

    def filter_today_episodes(self, episodes: List[SpotifyEpisode], return_others: bool = False) -> None:
        today_episodes = []
        others = []
        for episode in episodes:
            if CityDAOSpotify._is_date_in_ytd(episode.created_at):
                today_episodes.append(episode)
            else:
                others.append(episode)
        
        if return_others:
            return today_episodes, others
        
        return today_episodes

    def format_episodes(self, new_episodes: List[SpotifyEpisode], other_episodes: List[SpotifyEpisode]) -> str:
        template = f"📟 Here's latest CityDAO Podcast on [Spotify](https://open.spotify.com/show/4DqYWZyAMxUAL5o22caPSd)\\!\n\n"

        if len(new_episodes) == 0:
            template += f"🥱 There's no new episode from CityDAO Podcast\\. Stay Tuned\\!\n\n"
            return template.strip()
        else:
            template += f"🍻 There's {len(new_episodes)} new podcast episodes\\!\n\n"

        for i, episode in enumerate(new_episodes):
            template += f"👉 `{episode.name[:100]}...`\n"
            template += f"    [Listen to full Episode here]({episode.url})\n"
            template += f"    🎧 Duration: {episode.duration}\n"
            template += f"    ⏰Released on {episode.created_at.strftime('%d %b %Y %H:%M:%S UTC')}\n\n"

        if len(other_episodes) > 0:
            template += f"—————————————————————————\n\n"
            template += f"Checkout other episodes from [CityDAO Podcast](https://open.spotify.com/show/4DqYWZyAMxUAL5o22caPSd)\\!\n\n"

            for i, episode in enumerate(other_episodes):
                template += f"👉 `{episode.name[:100]}...`\n"
                template += f"    [Listen to full Episode here]({episode.url})\n"
                template += f"    🎧 Duration: {episode.duration}\n"
                template += f"    ⏰Released on {episode.created_at.strftime('%d %b %Y %H:%M:%S UTC')}\n\n"

        return template

    def get_daily_summary(self, n_episodes: int = 3) -> str:
        episodes = self.get_latest_episodes()
        new_episodes, other_episodes = self.filter_today_episodes(episodes, return_others=True)
        other_episodes = other_episodes[:max(0, n_episodes - len(new_episodes))]

        return self.format_episodes(new_episodes, other_episodes)
    