from enum import Enum


class ExcelColumnType(Enum):
    DISPLAY = "display"
    NUMBER = "number"
    DATE = "date"
    PERCENT = "percent"
    CHECKBOX = "checkbox"
    HIDDEN = "hidden"
    DROPDOWN = "dropdown"
    LINK = "link"
    FOLDER = "folder"
    TREE = "tree"
