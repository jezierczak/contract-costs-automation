from enum import Enum


class UnitOfMeasure(Enum):
    PIECE = "szt"        # sztuka
    METER = "m"          # metr
    SQUARE_METER = "m2"  # metr kwadratowy
    CUBIC_METER = "m3"   # metr sześcienny
    KILOGRAM = "kg"      # kilogram
    TON = "t"            # tona
    HOUR = "h"           # godzina
    DAY = "day"          # dzień
    SERVICE = "services"  # usługa