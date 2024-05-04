from typing import List, Optional

from sqlmodel import Field, Relationship

from .board import BoardBase, BoardInfoBase
from .hero import HeroBase
from .schedule import ScheduleBase
from .team import TeamBase
from .user import UserBase

#####################################################
#  ImportError: most likely due to a circular import
#  ==> 상호참조 모델은 한곳에서 정의해야 한다.


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class UserRead(UserBase):
    id: int


class BoardInfo(BoardInfoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class BoardInfoRead(BoardInfoBase):
    id: int


class Board(BoardBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # user: Optional["User"] = Relationship(back_populates="boards")


class BoardRead(BoardBase):
    id: int


class Schedule(ScheduleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ScheduleRead(ScheduleBase):
    id: int


class Hero(HeroBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # pydantic 은 Relationship 을 지원하지 않는다.
    # ==> field 로 인식하지 않는다.
    team: Optional["Team"] = Relationship(back_populates="heroes")


class HeroRead(HeroBase):
    id: int


class Team(TeamBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # pydantic 은 Relationship 을 지원하지 않는다.
    # ==> field 로 인식하지 않는다.
    heroes: List[Hero] = Relationship(back_populates="team")


class TeamRead(TeamBase):
    id: int  # override id to be required


################################################
#  Models with Relationships
#  https://sqlmodel.tiangolo.com/tutorial/fastapi/relationships/#models-with-relationships
#


class HeroReadWithTeam(HeroRead):
    team: Optional[TeamRead] = None


class TeamReadWithHeroes(TeamRead):
    heroes: List[HeroRead] = []
