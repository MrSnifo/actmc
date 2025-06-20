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
import asyncio
import inspect
import time

if TYPE_CHECKING:
    from typing import Callable, Any, Dict, List, Coroutine, TypeVar, Optional
    T = TypeVar('T', bound=Callable[..., Coroutine[Any, Any, None]])

__all__ = ('Loop', 'ticks')

import logging
_logger = logging.getLogger(__name__)


class Loop:
    """A tick-based task loop for asynchronous operations."""

    def __init__(self,
                 coro: Callable[..., Coroutine[Any, Any, None]],
                 tps: float = 60,
                 count: Optional[int] = None,
                 name: Optional[str] = None,
                 max_catchup: int = 5) -> None:
        if tps <= 0:
            raise ValueError("TPS must be positive")
        if max_catchup <= 0:
            raise ValueError("max_catchup must be positive")
        if not inspect.iscoroutinefunction(coro):
            raise TypeError(f'Expected coroutine function, not {type(coro).__name__!r}.')

        self.coro = coro
        self._target_tps = tps
        self._current_tps = tps
        self.tick_duration = 1.0 / tps
        self.count = count
        self.name = name or f"Loop-{coro.__name__}"
        self.max_catchup = max_catchup

        # State management
        self._running = False
        self._paused = False
        self._stopping = False
        self._task: Optional[asyncio.Task] = None
        self._tick_count = 0
        self._start_time = 0.0
        self._pause_time = 0.0
        self._total_pause_time = 0.0

        # Event callbacks
        self._on_start: Optional[Callable[[], Coroutine[Any, Any, None]]] = None
        self._on_stop: Optional[Callable[[], Coroutine[Any, Any, None]]] = None
        self._on_tick: Optional[Callable[[int], Coroutine[Any, Any, None]]] = None
        self._on_error: Optional[Callable[[Exception, int], Coroutine[Any, Any, None]]] = None

        # Tick control
        self._skip_next = False
        self._priority_queue: List[Callable[..., Coroutine[Any, Any, None]]] = []

    @property
    def tps(self) -> float:
        """Current ticks per second."""
        return self._current_tps

    @tps.setter
    def tps(self, value: float) -> None:
        """
        Set new TPS and adjust tick duration.

        Parameters
        ----------
        value: float
            New ticks per second value

        Raises
        ------
        ValueError
            If value <= 0
        """
        if value <= 0:
            raise ValueError("TPS must be positive")

        self._current_tps = value
        self.tick_duration = 1.0 / value

    @property
    def target_tps(self) -> float:
        """Target ticks per second."""
        return self._target_tps

    @property
    def is_running(self) -> bool:
        """Check if loop is running."""
        return self._running and not self._paused

    @property
    def is_paused(self) -> bool:
        """Check if loop is paused."""
        return self._paused

    @property
    def current_tick(self) -> int:
        """Get current tick number."""
        return self._tick_count

    @property
    def elapsed_time(self) -> float:
        """Get elapsed time since start (excluding pause time) in seconds."""
        if self._start_time == 0:
            return 0.0
        current_time = time.perf_counter()
        if self._paused:
            return self._pause_time - self._start_time - self._total_pause_time
        return current_time - self._start_time - self._total_pause_time

    def start(self, *args: Any, **kwargs: Any) -> asyncio.Task:
        """
        Start the loop.

        Parameters
        ----------
        *args: Any
            Positional arguments to pass to the coroutine
        **kwargs: Any
            Keyword arguments to pass to the coroutine

        Returns
        -------
        asyncio.Task
            The task running the loop

        Raises
        ------
        RuntimeError
            If loop is already running or fails to resume
        """
        if self._running:
            raise RuntimeError('Loop is already running.')

        if self._paused:
            result = self.resume()
            if result is None:
                raise RuntimeError("Failed to resume paused loop")
            return result

        self._running = True
        self._stopping = False
        self._tick_count = 0
        self._start_time = time.perf_counter()
        self._total_pause_time = 0.0

        self._task = asyncio.create_task(self._run(*args, **kwargs), name=self.name)

        if self._on_start:
            try:
                asyncio.create_task(self._on_start())
            except Exception as e:
                _logger.error(f"Error in on_start callback for loop '{self.name}': {e}")

        return self._task

    def stop(self) -> None:
        """Stop the loop gracefully."""
        if self._running:
            self._stopping = True

    def pause(self) -> None:
        """Pause the loop."""
        if self._running and not self._paused:
            self._paused = True
            self._pause_time = time.perf_counter()

    def resume(self) -> Optional[asyncio.Task]:
        """
        Resume from pause.

        Returns
        -------
        Optional[asyncio.Task]
            The task running the loop, or None if not paused
        """
        if self._paused:
            pause_duration = time.perf_counter() - self._pause_time
            self._total_pause_time += pause_duration
            self._paused = False
            return self._task
        return None

    def cancel(self) -> None:
        """Cancel the loop immediately."""
        if self._task and not self._task.done():
            self._task.cancel()

        self._running = False
        self._paused = False
        self._stopping = False

    def skip_next_tick(self) -> None:
        """Skip the next tick execution."""
        self._skip_next = True

    def queue_priority_task(self, task: Callable[..., Coroutine[Any, Any, None]]) -> None:
        """
        Queue a high-priority task to run on next tick.

        Parameters
        ----------
        task: Callable[..., Coroutine[Any, Any, None]]
            The coroutine function to run as priority task

        Raises
        ------
        Exception
            If task cannot be queued
        """
        try:
            self._priority_queue.append(task)
        except Exception as e:
            _logger.error(f"Failed to queue priority task for loop '{self.name}': {e}")
            raise

    async def _run(self, *args: Any, **kwargs: Any) -> None:
        """Internal loop runner implementation."""
        last_tick_time = time.perf_counter()
        accumulated_time = 0.0
        consecutive_errors = 0
        max_consecutive_errors = 10

        try:
            while not self._stopping:
                try:
                    # Handle pause
                    while self._paused and not self._stopping:
                        await asyncio.sleep(0.01)

                    if self._stopping:
                        break

                    tick_start = time.perf_counter()
                    current_time = tick_start
                    accumulated_time += current_time - last_tick_time

                    # Calculate how many ticks we need to catch up
                    ticks_to_run = min(int(accumulated_time / self.tick_duration), self.max_catchup)
                    if ticks_to_run == 0:
                        ticks_to_run = 1

                    # Run priority tasks first
                    while self._priority_queue:
                        try:
                            priority_task = self._priority_queue.pop(0)
                            await priority_task()
                        except Exception as e:
                            _logger.error(f"Error in priority task for loop '{self.name}': {e}")

                    # Execute ticks (catch-up mechanism)
                    for tick_iteration in range(ticks_to_run):
                        if self._stopping:
                            break

                        if self._skip_next:
                            self._skip_next = False
                            continue

                        try:
                            # Call on_tick callback
                            if self._on_tick:
                                await self._on_tick(self._tick_count)

                            # Execute main coroutine
                            await self.coro(self._tick_count, self.elapsed_time, *args, **kwargs)

                            # Reset error counter on successful tick
                            consecutive_errors = 0

                        except Exception as e:
                            consecutive_errors += 1
                            _logger.error(f"Error in tick {self._tick_count} of loop '{self.name}': {e}")

                            # Handle error via callback or break on too many consecutive errors
                            if self._on_error:
                                try:
                                    await self._on_error(e, self._tick_count)
                                except Exception as callback_error:
                                    _logger.error(f"Error in error callback for loop '{self.name}': {callback_error}")

                            if consecutive_errors >= max_consecutive_errors:
                                _logger.critical(f"Too many consecutive errors ({consecutive_errors})"
                                                 f" in loop '{self.name}', stopping")
                                self._stopping = True
                                break

                        self._tick_count += 1

                        if self.count and self._tick_count >= self.count:
                            self._stopping = True
                            break

                    # Sleep calculation with drift correction
                    accumulated_time -= ticks_to_run * self.tick_duration
                    next_tick_time = last_tick_time + (ticks_to_run * self.tick_duration)
                    sleep_time = next_tick_time - time.perf_counter()

                    if sleep_time > 0:
                        await asyncio.sleep(sleep_time)

                    last_tick_time = next_tick_time

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    _logger.error(f"Unexpected error in loop '{self.name}': {e}")

                    if self._on_error:
                        try:
                            await self._on_error(e, self._tick_count)
                        except Exception as callback_error:
                            _logger.error(f"Error in error callback for loop '{self.name}': {callback_error}")

                    # For unexpected errors, we break to avoid infinite loops
                    break

        except Exception as e:
            _logger.critical(f"Critical error in loop '{self.name}': {e}")
        finally:
            # Cleanup
            self._running = False
            self._paused = False
            self._stopping = False

            if self._on_stop:
                try:
                    await self._on_stop()
                except Exception as e:
                    _logger.error(f"Error in on_stop callback for loop '{self.name}': {e}")

    def on_start(self, callback: Callable[[], Coroutine[Any, Any, None]]) -> Callable[[], Coroutine[Any, Any, None]]:
        """
        Set callback for when loop starts.

        Parameters
        ----------
        callback: Callable[[], Coroutine[Any, Any, None]]
            The coroutine function to call on start

        Returns
        -------
        Callable[[], Coroutine[Any, Any, None]]
            The same callback function
        """
        self._on_start = callback
        return callback

    def on_stop(self, callback: Callable[[], Coroutine[Any, Any, None]]) -> Callable[[], Coroutine[Any, Any, None]]:
        """
        Set callback for when loop stops.

        Parameters
        ----------
        callback: Callable[[], Coroutine[Any, Any, None]]
            The coroutine function to call on stop

        Returns
        -------
        Callable[[], Coroutine[Any, Any, None]]
            The same callback function
        """
        self._on_stop = callback
        return callback

    def on_tick(self, callback: Callable[[int], Coroutine[Any, Any, None]]) -> Callable[[int],
                                                                               Coroutine[Any, Any, None]]:
        """
        Set callback called before each tick.

        Parameters
        ----------
        callback: Callable[[int], Coroutine[Any, Any, None]]
            The coroutine function to call before each tick

        Returns
        -------
        Callable[[int], Coroutine[Any, Any, None]]
            The same callback function
        """
        self._on_tick = callback
        return callback

    def on_error(self, callback: Callable[[Exception, int], Coroutine[Any, Any, None]]) -> Callable[[Exception, int],
    Coroutine[Any, Any, None]]:
        """
        Set callback for error handling.

        Parameters
        ----------
        callback: Callable[[Exception, int], Coroutine[Any, Any, None]]
            The coroutine function to call on error

        Returns
        -------
        Callable[[Exception, int], Coroutine[Any, Any, None]]
            The same callback function
        """
        self._on_error = callback
        return callback

    def get_info(self) -> Dict[str, Any]:
        """
        Get basic loop information.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing loop information with keys:
            - name: str - Loop name
            - running: bool - If loop is running
            - paused: bool - If loop is paused
            - current_tick: int - Current tick count
            - target_tps: float - Target ticks per second
            - current_tps: float - Current ticks per second
            - elapsed_time: float - Elapsed time in seconds
            - priority_queue_size: int - Size of priority queue
        """
        info = {
            'name': self.name,
            'running': self._running,
            'paused': self._paused,
            'current_tick': self._tick_count,
            'target_tps': self._target_tps,
            'current_tps': self._current_tps,
            'elapsed_time': self.elapsed_time,
            'priority_queue_size': len(self._priority_queue),
        }
        return info


def ticks(*,
          tps: float = 60,
          count: Optional[int] = None,
          name: Optional[str] = None,
          max_catchup: int = 5) -> Callable[[T], Loop]:
    """
    Decorator factory to create a tick-based loop.

    Parameters
    ----------
    tps: float
        Ticks per second
    count: Optional[int]
        Maximum number of ticks
    name: Optional[str]
        Custom name for the loop
    max_catchup: int
        Maximum ticks to catch up in one frame

    Returns
    -------
    Callable[[T], Loop]
        A decorator that converts a coroutine function into a Loop instance

    Raises
    ------
    ValueError
        If tps <= 0 or max_catchup <= 0
    """
    if tps <= 0:
        raise ValueError("TPS must be positive")
    if max_catchup <= 0:
        raise ValueError("max_catchup must be positive")

    def decorator(func: T) -> Loop:
        """
        The actual decorator that wraps the coroutine function.

        Parameters
        ----------
        func: T
            The coroutine function to wrap

        Returns
        -------
        Loop
            A configured Loop instance
        """
        loop_name = name or f"ticks-{func.__name__}"        
        return Loop(
            coro=func,
            tps=tps,
            count=count,
            name=loop_name,
            max_catchup=max_catchup
        )

    return decorator