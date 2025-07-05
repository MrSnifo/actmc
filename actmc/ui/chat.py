"""
The MIT License (MIT)

Copyright (c) 2025-present Snifo

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
import json
import re

if TYPE_CHECKING:
    from typing import Any, Optional, Dict, List, Union

__all__ = ('MessageEvent', 'Message')

class MessageEvent:
    """Represents a click or hover event in a chat message."""
    __slots__ = ('_action', '_value')

    def __init__(self, action: str, value: Union[str, Dict[str, Any]]) -> None:
        self._action: str = action
        self._value: Union[str, Dict[str, Any]] = value

    @property
    def action(self) -> str:
        """
        Get the event action type.

        Returns
        -------
        str
            The action type of this event (e.g., 'open_url', 'run_command').
        """
        return self._action

    @property
    def value(self) -> Union[str, Dict[str, Any]]:
        """
        Get the event value.

        Returns
        -------
        Union[str, Dict[str, Any]]
            The value associated with this event. Could be a string (for commands/URLs)
            or a dictionary (for complex hover events).
        """
        return self._value

    def __eq__(self, other: MessageEvent) -> bool:
        """
        Compare two MessageEvents for equality.

        Parameters
        ----------
        other: MessageEvent
            The object to compare with this MessageEvent.

        Returns
        -------
        bool
            True if the other object is a MessageEvent with identical action and value, False otherwise.
        """
        return self._action == other._action and self._value == other._value

    def __repr__(self) -> str:
        """
        Return the official string representation of the MessageEvent.

        Returns
        -------
        str
            A string that could be used to recreate the MessageEvent object.
        """
        return f"<MessageEvent action={self._action!r}, value={self._value!r}>"

class Message:
    """A class to handle Minecraft chat messages with full formatting and event support."""
    COLOR_MAP: Dict[str, str] = {
        'black': '§0', 'dark_blue': '§1', 'dark_green': '§2', 'dark_aqua': '§3',
        'dark_red': '§4', 'dark_purple': '§5', 'gold': '§6', 'gray': '§7',
        'dark_gray': '§8', 'blue': '§9', 'green': '§a', 'aqua': '§b',
        'red': '§c', 'light_purple': '§d', 'yellow': '§e', 'white': '§f',
        'reset': '§r'
    }

    CLICK_ACTIONS = {
        'open_url', 'run_command', 'suggest_command',
        'change_page', 'copy_to_clipboard'
    }

    HOVER_ACTIONS = {
        'show_text', 'show_item', 'show_entity', 'show_achievement'
    }

    HEX_COLOR_PATTERN: re.Pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')
    HEX_MAPPINGS: Dict[str, str] = {
        '#000000': '§0', '#0000aa': '§1', '#00aa00': '§2', '#00aaaa': '§3',
        '#aa0000': '§4', '#aa00aa': '§5', '#ffaa00': '§6', '#aaaaaa': '§7',
        '#555555': '§8', '#5555ff': '§9', '#55ff55': '§a', '#55ffff': '§b',
        '#ff5555': '§c', '#ff55ff': '§d', '#ffff55': '§e', '#ffffff': '§f'
    }

    __slots__ = ('_components', '_current_style', 'to_json')

    def __init__(self, data: Union[str, Dict[str, Any], List[Any]], to_json: bool = False) -> None:
        if to_json:
            data: Dict[str, Any] = json.loads(data)
        self._components: List[Dict[str, Any]] = []
        self._current_style: Dict[str, Any] = {}
        self._parse(data)

    def _parse(self, data: Union[str, Dict[str, Any], List[Any]]) -> None:
        """Parse input data into internal components."""
        if isinstance(data, str):
            self._components.append(self._create_text_component(data))
        elif isinstance(data, list):
            for item in data:
                self._parse(item)
        elif isinstance(data, dict):
            component = self._create_component_from_dict(data)
            if component:
                self._components.append(component)

    @staticmethod
    def _create_text_component(text: str, **kwargs: Any) -> Dict[str, Any]:
        """Create a basic text component."""
        return {
            'type': 'text',
            'text': text,
            **kwargs
        }

    def _create_translation_component(self, translate: str, with_params: List[Any],
                                      **kwargs: Any) -> Dict[str, Any]:
        """Create a translation component with parameters."""
        # Parse the with parameters to properly handle nested components
        parsed_params = []
        for param in with_params:
            if isinstance(param, dict):
                # This is a component, parse it properly
                parsed_component = self._create_component_from_dict(param)
                if parsed_component:
                    parsed_params.append(parsed_component)
            elif isinstance(param, list):
                # Parse list of components
                for item in param:
                    if isinstance(item, dict):
                        parsed_component = self._create_component_from_dict(item)
                        if parsed_component:
                            parsed_params.append(parsed_component)
                    else:
                        parsed_params.append(self._create_text_component(str(item)))
            else:
                # Simple text parameter
                parsed_params.append(self._create_text_component(str(param)))

        return {
            'type': 'translate',
            'translate': translate,
            'with': parsed_params,
            **kwargs
        }

    @staticmethod
    def _create_keybind_component(keybind: str, **kwargs: Any) -> Dict[str, Any]:
        """Create a keybind component."""
        return {
            'type': 'keybind',
            'keybind': keybind,
            **kwargs
        }

    @staticmethod
    def _create_score_component(score: Dict[str, str], **kwargs: Any) -> Dict[str, Any]:
        """Create a score component."""
        return {
            'type': 'score',
            'name': score.get('name', ''),
            'objective': score.get('objective', ''),
            'value': score.get('value', ''),
            **kwargs
        }

    @staticmethod
    def _create_selector_component(selector: str, **kwargs: Any) -> Dict[str, Any]:
        """Create a selector component."""
        return {
            'type': 'selector',
            'selector': selector,
            **kwargs
        }

    def _validate_click_event(self, data: Dict[str, Any]) -> Optional[MessageEvent]:
        """Validate and create a click event."""
        if not data or not isinstance(data, dict):
            return None

        action = data.get('action')
        value = data.get('value')

        if action not in self.CLICK_ACTIONS:
            return None

        return MessageEvent(action, value)

    def _validate_hover_event(self, data: Dict[str, Any]) -> Optional[MessageEvent]:
        """Validate and create a hover event."""
        if not data or not isinstance(data, dict):
            return None

        action = data.get('action')
        value = data.get('value')

        if action not in self.HOVER_ACTIONS:
            return None

        return MessageEvent(action, value)

    def _create_component_from_dict(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a component from dictionary data with proper style inheritance."""
        # Save current style before processing
        previous_style = self._current_style.copy()

        # Build new style with inheritance
        style = {
            'bold': data.get('bold', self._current_style.get('bold', False)),
            'italic': data.get('italic', self._current_style.get('italic', False)),
            'underlined': data.get('underlined', self._current_style.get('underlined', False)),
            'strikethrough': data.get('strikethrough', self._current_style.get('strikethrough', False)),
            'obfuscated': data.get('obfuscated', self._current_style.get('obfuscated', False)),
            'color': data.get('color', self._current_style.get('color')),
            'insertion': data.get('insertion', self._current_style.get('insertion'))
        }

        # Update current style for children
        self._current_style = style

        # Process events
        click_event = self._validate_click_event(data.get('clickEvent'))
        hover_event = self._validate_hover_event(data.get('hoverEvent'))

        # Process extra components
        extra = []
        for item in data.get('extra', []):
            if isinstance(item, dict):
                component = self._create_component_from_dict(item)
                if component:
                    extra.append(component)
            else:
                extra.append(self._create_text_component(str(item)))

        # Create the appropriate component
        component = None
        if 'text' in data:
            component = self._create_text_component(
                data['text'],
                style=style,
                click_event=click_event,
                hover_event=hover_event,
                extra=extra
            )
        elif 'translate' in data:
            component = self._create_translation_component(
                data['translate'],
                data.get('with', []),
                style=style,
                click_event=click_event,
                hover_event=hover_event,
                extra=extra
            )
        elif 'keybind' in data:
            component = self._create_keybind_component(
                data['keybind'],
                style=style,
                click_event=click_event,
                hover_event=hover_event,
                extra=extra
            )
        elif 'score' in data:
            component = self._create_score_component(
                data['score'],
                style=style,
                click_event=click_event,
                hover_event=hover_event,
                extra=extra
            )
        elif 'selector' in data:
            component = self._create_selector_component(
                data['selector'],
                style=style,
                click_event=click_event,
                hover_event=hover_event,
                extra=extra
            )

        # Restore previous style
        self._current_style = previous_style

        return component

    def _is_valid_color(self, color: str) -> bool:
        """Check if a color string is valid."""
        if not isinstance(color, str):
            return False
        return (color.lower() in self.COLOR_MAP or
                self.HEX_COLOR_PATTERN.match(color))

    def _get_format_codes(self, style: Dict[str, Any]) -> str:
        """Get Minecraft format codes for a style dictionary."""
        codes = []

        color = style.get('color')
        if color and self._is_valid_color(color):
            color_code = self.COLOR_MAP.get(color.lower())
            if color_code:
                codes.append(color_code)
            elif self.HEX_COLOR_PATTERN.match(color):
                codes.append(self.HEX_MAPPINGS.get(color.lower(), '§f'))

        if style.get('bold'):
            codes.append("§l")
        if style.get('italic'):
            codes.append("§o")
        if style.get('underlined'):
            codes.append("§n")
        if style.get('strikethrough'):
            codes.append("§m")
        if style.get('obfuscated'):
            codes.append("§k")

        return ''.join(codes)

    def _component_to_formatted_string(self, component: Dict[str, Any]) -> str:
        """Convert a component to formatted string with Minecraft codes and events."""
        result = self._get_format_codes(component.get('style', {}))

        # Handle click event
        click_event = component.get('click_event')
        if click_event:
            result += f"[click={click_event.action}:{click_event.value}]"

        # Handle hover event
        hover_event = component.get('hover_event')
        if hover_event:
            result += f"[hover={hover_event.action}:{hover_event.value}]"

        # Handle component content
        if component['type'] == 'text':
            result += component['text']
        elif component['type'] == 'translate':
            result += f"[{component['translate']}]"
            if component['with']:
                params = []
                for param in component['with']:
                    if isinstance(param, dict) and 'type' in param:
                        # This is a parsed component
                        params.append(self._component_to_formatted_string(param))
                    else:
                        params.append(str(param))
                result += f"({', '.join(params)})"
        elif component['type'] == 'keybind':
            result += f"[keybind:{component['keybind']}]"
        elif component['type'] == 'score':
            result += f"[score:{component['name']}:{component['objective']}]"
        elif component['type'] == 'selector':
            result += f"[selector:{component['selector']}]"

        # Add extra components
        for extra in component.get('extra', []):
            result += self._component_to_formatted_string(extra)

        return result

    def _component_to_plain_text(self, component: Dict[str, Any]) -> str:
        """Convert a component to plain text without formatting."""
        result = ""

        if component['type'] == 'text':
            result = component['text']
        elif component['type'] == 'translate':
            result = f"[{component['translate']}]"
            if component['with']:
                params = []
                for param in component['with']:
                    if isinstance(param, dict) and 'type' in param:
                        # This is a parsed component
                        params.append(self._component_to_plain_text(param))
                    else:
                        params.append(str(param))
                result += f"({', '.join(params)})"
        elif component['type'] == 'keybind':
            result = f"[keybind:{component['keybind']}]"
        elif component['type'] == 'score':
            result = f"[score:{component['name']}:{component['objective']}]"
        elif component['type'] == 'selector':
            result = f"[selector:{component['selector']}]"

        # Add extra components
        for extra in component.get('extra', []):
            result += self._component_to_plain_text(extra)

        return result

    @classmethod
    def create(cls, data: Union[str, Dict[str, Any], List[Any]]) -> Message:
        """
        Factory method to create a Message instance.

        Parameters
        ----------
        data: Union[str, Dict[str, Any], List[Any]]
            The message data to parse. Can be a string, dictionary (JSON component),
            or list of components.

        Returns
        -------
        Message
            A new Message instance containing the parsed components.
        """
        return cls(data)

    def to_formatted_string(self) -> str:
        """
        Convert all components to formatted string with Minecraft codes.

        Returns
        -------
        str
            The formatted message string with Minecraft formatting codes
            (e.g., §a for green) and event markers.
        """
        return ''.join(self._component_to_formatted_string(comp) for comp in self._components)

    def to_plain_text(self) -> str:
        """
        Convert all components to plain text without formatting.

        Returns
        -------
        str
            The message content without any formatting or style information.
        """
        return ''.join(self._component_to_plain_text(comp) for comp in self._components)

    def get_click_commands(self) -> List[str]:
        """
        Get all click commands from all components.

        Returns
        -------
        List[str]
            A list of all command strings from click events of type 'run_command' or 'suggest_command'.
        """
        commands = []
        command_actions = {'run_command', 'suggest_command'}

        def _extract_from_component(comp: Dict[str, Any]) -> None:
            click_event = comp.get('click_event')
            if click_event and click_event.action in command_actions:
                commands.append(str(click_event.value))

            # Check extra components
            for extra_comp in comp.get('extra', []):
                _extract_from_component(extra_comp)

            # Check with parameters for translation components
            if comp.get('type') == 'translate':
                for param in comp.get('with', []):
                    if isinstance(param, dict) and 'type' in param:
                        _extract_from_component(param)

        for component in self._components:
            _extract_from_component(component)

        return commands

    def get_click_events(self) -> List[MessageEvent]:
        """
        Get all click events from the message.

        Returns
        -------
        List[MessageEvent]
            A list of all MessageEvent objects representing click actions in the message.
        """
        events = []

        def _extract_events(comp: Dict[str, Any]) -> None:
            if comp.get('click_event'):
                events.append(comp['click_event'])

            # Check extra components
            for extra_comp in comp.get('extra', []):
                _extract_events(extra_comp)

            # Check with parameters for translation components
            if comp.get('type') == 'translate':
                for param in comp.get('with', []):
                    if isinstance(param, dict) and 'type' in param:
                        _extract_events(param)

        for component in self._components:
            _extract_events(component)

        return events

    def get_hover_events(self) -> List[MessageEvent]:
        """
        Get all hover events from the message.

        Returns
        -------
        List[MessageEvent]
            A list of all MessageEvent objects representing hover actions in the message.
        """
        events = []

        def _extract_events(comp: Dict[str, Any]) -> None:
            if comp.get('hover_event'):
                events.append(comp['hover_event'])

            # Check extra components
            for extra_comp in comp.get('extra', []):
                _extract_events(extra_comp)

            # Check with parameters for translation components
            if comp.get('type') == 'translate':
                for param in comp.get('with', []):
                    if isinstance(param, dict) and 'type' in param:
                        _extract_events(param)

        for component in self._components:
            _extract_events(component)

        return events

    def get_components_count(self) -> int:
        """Get the total number of components in the message."""
        def _count_components(comp: Dict[str, Any]) -> int:
            count = 1

            # Count extra components
            count += sum(_count_components(extra) for extra in comp.get('extra', []))

            # Count with parameters for translation components
            if comp.get('type') == 'translate':
                for param in comp.get('with', []):
                    if isinstance(param, dict) and 'type' in param:
                        count += _count_components(param)

            return count

        return sum(_count_components(comp) for comp in self._components)

    def __str__(self) -> str:
        """
        Return the formatted string representation of the message.

        Returns
        -------
        str
            Same as to_formatted_string().
        """
        return self.to_formatted_string()

    def __repr__(self) -> str:
        """
        Return the official string representation of the Message object.

        Returns
        -------
        str
            A string showing basic information about the message.
        """
        return f"<Message components={len(self._components)}>"

    def __len__(self) -> int:
        """
        Get the length of the formatted string.

        Returns
        -------
        int
            The length of the formatted string.
        """
        return len(self.to_formatted_string())

    def __bool__(self) -> bool:
        """
        Check if the message contains any content.

        Returns
        -------
        bool
            True if the message contains any components, False otherwise.
        """
        return bool(self._components)

    def __eq__(self, other: Message) -> bool:
        """
        Compare two messages for equality based on plain text content.

        Parameters
        ----------
        other: Message
            The object to compare with.

        Returns
        -------
        bool
            True if the other object is a Message with identical plain text content, False otherwise.
        """
        return self.to_plain_text() == other.to_plain_text()
