from dataclasses import dataclass
import json
from enum import Enum, auto
from MineSweeper_Difficulty import Difficulty

class GameMessageType(Enum):
    READY_STATE = auto()
    FIRST_CELL_REVEAL = auto()
    CELL_REVEAL = auto()
    TOGGLE_FLAG = auto()
    CHORD_CLICK = auto()
    CHORD_PRESS = auto()
    CHORD_RELEASE = auto()
    GAME_OVER = auto()
    GAME_COMPLETE = auto()
    RESET = auto()
    CHANGE_DIFFICULTY = auto()

@dataclass
class GameMessage:
    type: GameMessageType
    data: dict
    
    def to_json(self) -> str:
        # 傳送自定義類別 Difficulty
        data = self.data.copy()
        if "difficulty" in data and isinstance(data["difficulty"], Difficulty):
            data["difficulty"] = data["difficulty"].name
        return json.dumps({
            "type": self.type.name,
            "data": data
        })
    
    @staticmethod
    def from_json(json_str: str) -> 'GameMessage':
        data = json.loads(json_str)
        message_data = data['data']
        if "difficulty" in message_data:
            message_data["difficulty"] = Difficulty[message_data["difficulty"]]
            
        return GameMessage(
            type=GameMessageType[data["type"]],
            data=data["data"]
        )