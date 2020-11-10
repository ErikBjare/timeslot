from datetime import datetime, timedelta
from typing import Optional, Union


class Timeslot:
    # Inspired by: http://www.codeproject.com/Articles/168662/Time-Period-Library-for-NET
    def __init__(self, start: datetime, end: datetime) -> None:
        # TODO: Introduce once tested in production (where negative duration events might occur)
        # if start > end:
        #     raise ValueError("Timeslot cannot have negative duration, start '{}' came after end '{}'".format(start, end))
        self.start = start
        self.end = end

    def __repr__(self) -> str:
        return "<Timeslot(start={}, end={})>".format(self.start, self.end)

    @property
    def duration(self) -> timedelta:
        return self.end - self.start

    def overlaps(self, other: "Timeslot") -> bool:
        """Checks if this timeslot is overlapping partially or entirely with another timeslot"""
        return (
            self.start <= other.start < self.end
            or self.start < other.end <= self.end
            or self in other
        )

    def intersects(self, other: "Timeslot") -> bool:
        """Alias for overlaps"""
        return self.overlaps(other)

    def contains(self, other: Union[datetime, "Timeslot"]) -> bool:
        """Checks if this timeslot contains the entirety of another timeslot or a datetime"""
        if isinstance(other, Timeslot):
            return self.start <= other.start and other.end <= self.end
        elif isinstance(other, datetime):
            return self.start <= other <= self.end
        else:
            raise TypeError("argument of invalid type '{}'".format(type(other)))

    def __contains__(self, other: Union[datetime, "Timeslot"]) -> bool:
        return self.contains(other)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Timeslot):
            return self.start == other.start and self.end == other.end
        else:
            return False

    def __lt__(self, other: object) -> bool:
        # implemented to easily allow sorting of a list of timeslots
        if isinstance(other, Timeslot):
            return self.start < other.start
        else:
            raise TypeError(
                "operator not supported between instaces of '{}' and '{}'".format(
                    type(self), type(other)
                )
            )

    def intersection(self, other: "Timeslot") -> Optional["Timeslot"]:
        """Returns the timeslot contained in both slots"""
        # https://stackoverflow.com/posts/3721426/revisions
        if self.contains(other):
            # Entirety of other is within self
            return other
        elif self.start <= other.start < self.end:
            # End part of self intersects
            return Timeslot(other.start, self.end)
        elif self.start < other.end <= self.end:
            # Start part of self intersects
            return Timeslot(self.start, other.end)
        elif other.contains(self):
            # Entirety of self is within other
            return self
        return None

    def adjacent(self, other: "Timeslot") -> bool:
        """Iff timeslots are exactly next to each other, return True."""
        return self.start == other.end or self.end == other.start

    def gap(self, other: "Timeslot") -> Optional["Timeslot"]:
        """If slots are separated by a non-zero gap, return the gap as a new timeslot, else None"""
        if self.end < other.start:
            return Timeslot(self.end, other.start)
        elif other.end < self.start:
            return Timeslot(other.end, self.start)
        else:
            return None

    def union(self, other: "Timeslot") -> "Timeslot":
        if not self.gap(other):
            return Timeslot(min(self.start, other.start), max(self.end, other.end))
        else:
            raise Exception("Timeslots must not have a gap if they are to be unioned")
