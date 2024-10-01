from enum import Enum


class ContractEnum(Enum):
    B2B = "B2B"
    UOP = "Employement Contract"
    UZ = "Mandate Contract"
    UoD = "Work Contract"


class WorkModeEnum(Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"


class ExperienceEnum(Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"


class JobTypeEnum(Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
