from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, List, Optional

import pytz
from googleapiclient.discovery import build


@dataclass
class CalendarEvent(object):
    url: str
    summary: str
    creator: str
    start_time: datetime
    end_time: datetime
    meeting_url: Optional[str] = None

    def __repr__(self) -> str:
        return f"CalendarEvent(summary='{self.summary}', start_time={self.start_time.strftime('%Y-%m-%dT%H:%M:%SZ')}, end_time={self.end_time.strftime('%Y-%m-%dT%H:%M:%SZ')}"


class CityDAOCalendar(object):

    def __init__(self, google_apikey: str) -> None:
        self.calendar_id = "c_4r6hnu78hifcmgimcgm0huhc6k@group.calendar.google.com"
        self.service = build("calendar", "v3", developerKey=google_apikey)
        self.timezone = "UTC"
        self.url = f"https://calendar.google.com/calendar/u/0/embed?src=c_4r6hnu78hifcmgimcgm0huhc6k@group.calendar.google.com&ctz={self.timezone}"

    def get_today_events(self) -> Any:
        today = datetime.now()
        start_time = today.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=pytz.UTC)
        end_time = start_time + timedelta(days=1)
        events = self.service.events().list(
            calendarId=self.calendar_id, 
            timeMin=start_time.strftime("%Y-%m-%dT%H:%M:%SZ"), 
            timeMax=end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            orderBy="startTime",
            singleEvents=True,
            timeZone=self.timezone
        ).execute()

        return [
            CalendarEvent(
                url=event["htmlLink"],
                summary=event["summary"],
                creator=event["creator"]["email"],
                start_time=datetime.strptime(event["start"]["dateTime"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.timezone(self.timezone)),
                end_time=datetime.strptime(event["end"]["dateTime"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.timezone(self.timezone)),
                meeting_url=event.get("hangoutLink", None)
            )
            for event in events["items"]
        ]

    def format_events(self, events: List[CalendarEvent]) -> str:
        if len(events) == 0:
            return f"🗓 There's no CityDAO Event today!\n\nEnjoy your holiday🍻"

        template = f"🗓 There're {len(events)} events on [CityDAO Calendar]() today\\!\n\n"

        for event in events:
            template += f"👉 `{event.summary}`\n"
            template += f"  🕰 Time: {event.start_time.strftime('%H:%M:%S')} \\- {event.end_time.strftime('%H:%M:%S')}\n"
            template += f"  🧑‍💻 Creator: `{event.creator}`\n"
            if event.meeting_url is not None:
                template += f"  🔗 Join meeting [here]({event.meeting_url})\n\n"

        template += f"🧋 Have a wonderful day Citizen\\!"

        return template

    def get_daily_summary(self) -> str:
        today_events = self.get_today_events()
        return self.format_events(today_events)
