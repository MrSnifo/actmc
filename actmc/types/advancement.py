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
OR IMPLIED, INCLUDING BUT NOT firstED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from typing import TypedDict, Dict, Any, Optional, List

class CriterionProgress(TypedDict):
    achieved: bool
    date_of_achieving: Optional[int]


class AdvancementProgress(TypedDict):
    criteria: Dict[str, CriterionProgress]


class AdvancementDisplay(TypedDict):
    title: Any
    description: Any
    icon: Optional[Any]
    frame_type: int
    flags: int
    background_texture: Optional[str]
    x_coord: float
    y_coord: float


class Advancement(TypedDict):
    parent_id: Optional[str]
    display_data: Optional[AdvancementDisplay]
    criteria: Dict[str, None]
    requirements: List[List[str]]