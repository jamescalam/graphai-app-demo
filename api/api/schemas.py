from pydantic import BaseModel


class Interaction(BaseModel):
    message: str
    chat_history: list[dict[str, str]]
