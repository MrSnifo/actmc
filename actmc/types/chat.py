from typing import Union, List, TypedDict, NotRequired, Literal


DISPLAY = Literal['chat', 'system', 'game']

class ClickEvent(TypedDict):
    action: Literal['open_url', 'open_file', 'run_command', 'suggest_command', 'change_page', 'twitch_user_info']
    value: str

class HoverEvent(TypedDict):
    action: Literal['show_text', 'show_item', 'show_entity', 'show_achievement']
    value: Union[str, 'ChatComponent']

class ScoreComponent(TypedDict):
    name: str
    objective: str
    value: NotRequired[str]

class ChatComponent(TypedDict, total=False):
    text: str
    translate: str
    keybind: str
    score: ScoreComponent
    selector: str
    with_: List['ChatComponent']  # for translate components
    extra: List['ChatComponent']
    color: Literal['black', 'dark_blue', 'dark_green', 'dark_aqua', 'dark_red', 'dark_purple', 
                   'gold', 'gray', 'dark_gray', 'blue', 'green', 'aqua', 'red', 'light_purple', 
                   'yellow', 'white', 'reset']
    bold: bool
    italic: bool
    underlined: bool
    strikethrough: bool
    obfuscated: bool
    insertion: str
    clickEvent: ClickEvent
    hoverEvent: HoverEvent