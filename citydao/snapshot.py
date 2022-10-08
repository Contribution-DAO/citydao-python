import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import requests

from citydao.utils import Web3Address


class ProposalStatus(Enum):
    ACTIVE = "active"
    CLOSED = "closed"


@dataclass
class SnapshotSpace(object):
    id: str
    name: str
    network: int
    symbol: str
    members: List[str] = field(default_factory=lambda: [])
    about: Optional[str] = None

    def __post_init__(self):
        self.members = [
            Web3Address(member, resolve_ens=True)
            for member in self.members
        ]

    def add_member(self, address: str) -> None:
        self.members.append(Web3Address(address, resolve_ens=True))

    def __repr__(self) -> str:
        return f"SnapshotSpace(name='{self.name}', symbol='{self.symbol}')"


@dataclass
class SnapshotProposal(object):
    id: str
    title: str
    body: str
    choices: List[str]
    start: int
    end: int
    state: Union[str, ProposalStatus]
    author: Web3Address
    snapshot: str
    quorum: int
    scores: Optional[Dict[str, int]] = None
    
    def __post_init__(self) -> None:
        if isinstance(self.state, str):
            self.state = ProposalStatus(self.state)
        self.url = f"https://snapshot.org/#/daocity.eth/proposal/{self.id}"

    def get_votes(self) -> None:
        self.votes = SnapshotAPI().get_votes(self)
        return self.votes

    def __repr__(self) -> str:
        return f"CityDAOProposal(title='{self.title}', author={self.author.address})"


@dataclass
class SnapshotVote(object):
    voter: Web3Address
    created: int
    choice: int

    def __repr__(self) -> str:
        return f"Vote({self.choice})"


class SnapshotAPI(object):

    def __init__(self) -> None:
        self.endpoint = "https://hub.snapshot.org/graphql"
        self.space = "daocity.eth"
        self.url = f"https://snapshot.org/#/{self.space}"

    def query_graphql(self, query: str) -> None:
        response = requests.post(self.endpoint, json={"query": query})
        return json.loads(response.text)

    def get_votes(self, proposal: SnapshotProposal) -> Any:
        query = """query Votes {{
                    votes (
                        skip: 0
                        where: {{
                            proposal: "{proposal_id}"
                        }}
                        orderBy: "created",
                        orderDirection: desc
                    ) {{
                        id
                        voter
                        created
                        choice
                        proposal {{
                            id
                            choices
                        }}
                    }}
                }}""".format(proposal_id=proposal.id)

        response = self.query_graphql(query)
        
        votes = []
        for vote in response["data"]["votes"]:
            choices = vote["proposal"]["choices"]
            choice = choices[vote["choice"] - 1]  # choice index start with 1
            votes.append(SnapshotVote(
                voter=Web3Address(vote["voter"]),
                created=vote["created"],
                choice=choice
            ))
        return votes

    def get_space_info(self) -> SnapshotSpace:
        query = """query {
                    space(id: "daocity.eth") {
                        id
                        name
                        about
                        network
                        symbol
                        members
                    }
                }
                """

        response = self.query_graphql(query)
        return SnapshotSpace(**response["data"]["space"])

    def get_proposals(
        self, 
        status: Optional[ProposalStatus] = None,
        resolve_author_ens: bool = False
    ) -> List[SnapshotProposal]:
        query_status = "" if status is None else f'state: "{status.value}",'

        query = """query Proposals {{
            proposals (
                skip: 0,
                where: {{
                    space_in: ["{space}"],
                    {status}
                }},
                orderBy: "created",
                orderDirection: desc
            ) {{
                id
                title
                body
                choices
                start
                end
                snapshot
                state
                scores
                scores_by_strategy
                scores_total
                quorum
                author
            }}
        }}""".format(
            space=self.space,
            status=query_status
        )

        response = self.query_graphql(query)
        proposals = [
            SnapshotProposal(
                id=proposal["id"],
                title=proposal["title"],
                body=proposal["body"],
                choices=proposal["choices"],
                start=proposal["start"],
                end=proposal["end"],
                snapshot=proposal["snapshot"],
                state=proposal["state"],
                author=Web3Address(proposal["author"], resolve_ens=resolve_author_ens),
                scores={choice: int(score) for choice, score in zip(proposal["choices"], proposal["scores"])},
                quorum=proposal["quorum"]
            )
            for proposal in response["data"]["proposals"]
        ]
        return proposals

    def format_active_proposals(self, proposals: List[SnapshotProposal]) -> Optional[str]:
        template = f"🗳 [CityDAO Snapshot]({self.url}) have {len(proposals)} active proposal\(s\)\\!\n\n"

        if len(proposals) == 0:
            return None

        for proposal in proposals:
            template += f"👉 [`{proposal.title}`]({proposal.url})\n"

            template += "    📊 "
            for i, (choice, count) in enumerate(proposal.scores.items()):
                template += f"{choice}: {count}"
                if i != len(proposal.scores) - 1:
                    template += f"\t"
            template += "\n"

            template += f"   🧿 Quorum: {sum(proposal.scores.values())}  / {proposal.quorum}\n"
            deadline = datetime.utcfromtimestamp(proposal.end)
            time_delta = (deadline - datetime.today())
            days_left = time_delta.days
            seconds_left = time_delta.seconds
            minutes_left, _ = divmod(seconds_left, 60)
            hours_left, minutes_left = divmod(minutes_left, 60)
            template += f"   ⏰ Deadline: {deadline.strftime('%d %b %Y %H:%M:%S UTC')}\n"
            template += f"           \({int(days_left)} days {int(hours_left)} hours {int(minutes_left)} minutes left\\!\)\n"
            template += f"   🟢 Cast your vote [here]({proposal.url})\n\n"

        template += f"📝 Be sure to vote if you're a Citizen\\!"
        return template

    def get_daily_summary(self) -> str:
        active_proposals = self.get_proposals(ProposalStatus.ACTIVE)
        return self.format_active_proposals(active_proposals)
