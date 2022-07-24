# CityDAO Utility Bot + Python package
A utility python package to fetch **everything** about CityDAO's info. 

## 🧰 Dependencies
- Python >= 3.10

<details><summary><b>From source</b></summary>

1. _Activate virtual environment (Optional)_
    ```bash
    python3 -m venv citydao.venv
    source citydao.venv/bin/activate
    ```

2. _Install via `setup.py`_
    ```bash
    python setup.py install
    ```

</details>

<details><summary><b>From pypi</b></summary>

*TBD*

</details>

## 💻 Usage
There are 4 main usage for this repository

### Prepare `.env` files
Prepare `.env` files according to what was shown in [`.env.example`](./.env.example).
- Get google API key [here](https://support.google.com/googleapi/answer/6158862?hl=en)
- Get twitter API key/secret [here](https://developer.twitter.com/en/portal/register/welcome)
- Get telegram API key for bot [here](https://core.telegram.org/bots)

<details><summary><b>🤖 Run a telegram bot</b></summary>

Please see example at [`run_bot.py`](./run_bot.py)

</details>

<details><summary><b>📟 Fetch latest tweets</b></summary>

```python
from citydao.tweets import CityDAOTwitter


apikey = "your_twitter_apikey"
api_secret = "your_twitter_api_secret"
twitter = CityDAOTwitter(apikey, api_secret)
tweets = twitter.fetch_recent_tweets()
today_tweets = twitter.filter_today_tweets(tweets)
```

</details>

<details><summary><b>🗓 Fetch calendar events</b></summary>

```python
from citydao.calendar import CityDAOCalendar

google_apikey = "your_google_api_key"
calendar = CityDAOCalendar(google_apikey=google_apikey)

today_events = calendar.get_today_events()
```

</details>

<details><summary><b>🏦 Get current treasury balance</b></summary>

```python
from citydao.treasury import CityDAOTreasury

treasury = CityDAOTreasury()
balance = treasury.get_balance()

# balance = {
#   "WETH": XXX,
#   "USDC": YYY,
#   "ETH": ZZZ
# }
```

</details>

<details><summary><b>🗳 Get CityDAO's proposals</b></summary>

```python
from citydao.snapshot import SnapshotAPI, ProposalStatus

snapshot = SnapshotAPI()
proposals = snapshot.get_proposals()
active_proposals = snapshot.get_proposals(status=ProposalStatus.ACTIVE)
closed_proposals = snapshot.get_proposals(status=ProposalStatus.CLOSED)

for proposal in proposals:
    # get detailed votes for each proposal
    votes = proposal.get_votes()
```

</details>

## 🔬 Contributing
Feels free to fork this repository and create a pull request!

## 🧙‍♂️ Author
Chompakorn Chaksangchaichot
