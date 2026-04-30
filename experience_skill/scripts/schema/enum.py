from enum import Enum


class ExperienceType(Enum):
    SKILL = "skill"
    WIKI = "wiki"


class ExperienceStatus(Enum):
    EXISTED = "existed"
    DELETED = "deleted"
