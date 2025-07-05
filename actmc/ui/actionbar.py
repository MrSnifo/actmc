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

__all__ = ('Title',)

class Title:
    """
    Minecraft Title representation and state manager.

    Attributes
    ----------
    title: str
        Current title text
    subtitle: str
        Current subtitle text
    action_bar: str
        Current action bar text
    fade_in: int
        Fade in time in ticks
    stay: int
        Stay time in ticks
    fade_out: int
        Fade out time in ticks
    visible: bool
        Whether the title is currently visible
    """

    __slots__ = ('title', 'subtitle', 'action_bar', 'fade_in', 'stay', 'fade_out', 'visible')

    def __init__(self, title: str = "", subtitle: str = "", action_bar: str = "",
                 fade_in: int = 10, stay: int = 70, fade_out: int = 20) -> None:
        self.title: str = title
        self.subtitle: str = subtitle
        self.action_bar: str = action_bar
        self.fade_in: int = fade_in
        self.stay: int = stay
        self.fade_out: int = fade_out
        self.visible: bool = False

    def set_title(self, title: str) -> None:
        """
        Set the main title text.

        Parameters
        ----------
        title: str
            The title text to display
        """
        self.title = title

    def set_subtitle(self, subtitle: str) -> None:
        """
        Set the subtitle text.

        Parameters
        ----------
        subtitle: str
            The subtitle text to display
        """
        self.subtitle = subtitle

    def set_action_bar(self, action_bar: str) -> None:
        """
        Set the action bar text.

        Parameters
        ----------
        action_bar: str
            The action bar text to display
        """
        self.action_bar = action_bar

    def set_times(self, fade_in: int, stay: int, fade_out: int) -> None:
        """
        Set the timing parameters for title display.

        Parameters
        ----------
        fade_in: int
            Ticks to spend fading in
        stay: int
            Ticks to keep the title displayed
        fade_out: int
            Ticks to spend fading out
        """
        self.fade_in = fade_in
        self.stay = stay
        self.fade_out = fade_out

    def show(self) -> None:
        """
        Show the title.
        """
        self.visible = True

    def hide(self) -> None:
        """
        Hide the title.
        """
        self.visible = False

    def reset(self) -> None:
        """
        Reset the title to default state.
        """
        self.title = ""
        self.subtitle = ""
        self.action_bar = ""
        self.fade_in = 10
        self.stay = 70
        self.fade_out = 20
        self.visible = False

    def total_duration_ticks(self) -> int:
        """
        Get total duration of title display in ticks.

        Returns
        -------
        int
            Total duration (fade_in + stay + fade_out)
        """
        return self.fade_in + self.stay + self.fade_out

    def total_duration_seconds(self) -> float:
        """
        Get total duration of title display in seconds.

        Returns
        -------
        float
            Total duration in seconds (20 ticks = 1 second)
        """
        return self.total_duration_ticks() / 20.0

    def has_content(self) -> bool:
        """
        Check if title has any content to display.

        Returns
        -------
        bool
            True if title, subtitle, or action bar has content
        """
        return bool(self.title or self.subtitle or self.action_bar)

    def is_visible(self) -> bool:
        """
        Check if title should be visible.

        Returns
        -------
        bool
            True if visible and has content
        """
        return self.visible and self.has_content()

    def __repr__(self) -> str:
        return f"<Title title='{self.title}', subtitle='{self.subtitle}', visible={self.visible}>"