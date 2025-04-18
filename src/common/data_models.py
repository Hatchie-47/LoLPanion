from pydantic import BaseModel, computed_field
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum


class Server(BaseModel):
    id: int
    cluster: str
    server: str


class Tag(str, Enum):
    INTER = 'INTER'
    FLAMER = 'FLAMER'
    TILTER = 'TILTER'
    UNDERPERFORMER = 'UNDERPERFORMER'
    OVERPERFORMER = 'OVERPERFORMER'
    ONETRICK = 'ONETRICK'


class Severity(str, Enum):
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'


class Mastery(BaseModel):
    champion_id: int
    mastery_points: int


class AssignedTag(BaseModel):
    tag: Tag
    added: Optional[datetime] = None
    severity: Severity
    note: str


class Role(BaseModel):
    id: int
    name: str


class Alert(BaseModel):
    name: str
    detail: str
    priority: int
    color: str


class Summoner(BaseModel):
    puu_id: Optional[str] = None
    name: str
    tagline: str
    server: Server
    profile_icon: Optional[int] = None
    revision_date: Optional[datetime] = None
    summoner_level: Optional[int] = None
    tags: Optional[list[AssignedTag]] = None


class ParticipantStats(BaseModel):
    kills: int
    deaths: int
    assists: int
    item0: int
    item1: int
    item2: int
    item3: int
    item4: int
    item5: int
    item6: int
    total_gold: int
    cs: int


class Participant(BaseModel):
    summoner: Summoner
    team_red: bool
    role: Optional[Role] = None
    summ_spell1: int
    summ_spell2: int
    champion: int
    mastery_points: Optional[int] = None
    bot: Optional[bool] = None
    primary_runes: int
    secondary_runes: int
    runes: list[int]
    small_runes: Optional[list[int]] = None
    stats: Optional[ParticipantStats] = None
    tags: Optional[list[AssignedTag]] = None
    alerts: Optional[list[Alert]] = None
    has_history: Optional[bool] = None


class MatchDetail(BaseModel):
    match_creation: datetime
    match_end: Optional[datetime] = None
    match_duration: Optional[timedelta]
    game_version: str
    winning_team_red: Optional[bool] = None
    match_timeline: Optional[dict] = None


class Match(BaseModel):
    server: Server
    match_id: Optional[int] = None
    match_type: Optional[str] = None
    match_start: Optional[datetime] = None
    participants: Optional[list[Participant]] = None
    match_detail: Optional[MatchDetail] = None

    @computed_field
    @property
    def full_match_id(self) -> str:
        return self.server.server + '_' + str(self.match_id)
