from dataclasses import dataclass
import datetime
import uuid

@dataclass
class Character:
    id: uuid.UUID
    name: str
    elo: float

def create_character(name: str, elo: float = 400) -> Character:
    id: uuid.UUID = uuid.uuid7()
    return Character(id, name, elo)


@dataclass
class Card:
    id: uuid.UUID
    object_key: str
    created_at: datetime.datetime

def create_card(object_key: str):
    id: uuid.UUID = uuid.uuid7()
    return Card(id, object_key, datetime.datetime.now(datetime.timezone.utc))


@dataclass
class CharacterCard:
    id: uuid.UUID
    card_id: uuid.UUID
    character_id: uuid.UUID

def create_character_card(card_id: uuid.UUID, character_id: uuid.UUID):
    id: uuid.UUID = uuid.uuid7()
    return CharacterCard(id, card_id, character_id)