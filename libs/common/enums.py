from enum import Enum


class coreEnum(Enum):
    HARTABERFAIR = 1
    INASNACHT = 2
    ROCKPALAST = 3
    HDTRAILERS = 4


class tagEnum(Enum):
    NONE = 0
    SIGNLANGUAGE = 1
    MUSICCLIP = 2
    INTERVIEW = 3
    UNPLUGGED = 4
    LIVEPREVIEW = 5


class subItemTagEnum(Enum):
    NONE = 0
    TRAILER = 1
    TEASER = 2
    CLIP = 3


class listEnum(Enum):
    HDT_MOSTWATCHEDWEEK = 1
    HDT_MOSTWATCHEDTODAY = 2
    HDT_TOPTEN = 3
    HDT_OPENING = 4
    HDT_COMINGSOON = 5
