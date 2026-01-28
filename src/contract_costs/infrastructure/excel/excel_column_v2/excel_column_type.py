from enum import Enum


class ExcelColumnType(Enum):
    DISPLAY = "display"
    PERCENT = "percent"
    CHECKBOX = "checkbox"
    HIDDEN = "hidden"
    DROPDOWN = "dropdown"
    LINK = "link"
    FOLDER = "folder"
    TREE = "tree"
