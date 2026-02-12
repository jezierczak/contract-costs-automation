from enum import Enum


class ExcelColumnType(Enum):
    PERCENT = "percent"
    DISPLAY = "display"
    CHECKBOX = "checkbox"
    HIDDEN = "hidden"
    DROPDOWN= "dropdown"
    LINK = "link"
    FOLDER = "folder"
    #v2 columns added
    NUMBER = "number"
    DATE = "date"
    TREE = "tree"
