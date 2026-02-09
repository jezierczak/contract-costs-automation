from pydantic import BaseModel


class DocumentView(BaseModel):
    filename: str
    file_path: str
    document_type_: str
