from datetime import datetime, timedelta

import pytest
from timeslot import Timeslot


def test_intersection_start():
    now = datetime.now()
    tp1 = Timeslot(now, now + timedelta(hours=1))
    tp2 = Timeslot(now - timedelta(minutes=10), now + timedelta(minutes=50))
    assert tp1.intersection(tp2).duration == timedelta(minutes=50)
    assert tp2.intersection(tp1).duration == timedelta(minutes=50)


def test_intersection_end():
    now = datetime.now()
    tp1 = Timeslot(now, now + timedelta(hours=1))
    tp2 = Timeslot(now + timedelta(minutes=10), now + timedelta(hours=1))
    assert tp1.intersection(tp2).duration == timedelta(minutes=50)
    assert tp2.intersection(tp1).duration == timedelta(minutes=50)


def test_intersection_entire():
    now = datetime.now()
    tp1 = Timeslot(now, now + timedelta(hours=1))
    tp2 = Timeslot(now - timedelta(minutes=10), now + timedelta(minutes=70))
    assert tp1.intersection(tp2).duration == timedelta(minutes=60)
    assert tp2.intersection(tp1).duration == timedelta(minutes=60)


def test_intersection_none():
    now = datetime.now()
    tp1 = Timeslot(now, now + timedelta(hours=1))
    tp2 = Timeslot(now - timedelta(hours=1), now)
    assert tp1.intersection(tp2) is None
    assert tp2.intersection(tp1) is None


def test_contains():
    now = datetime.now()

    tp1 = Timeslot(now - timedelta(hours=1), now + timedelta(hours=1))
    tp2 = Timeslot(now, now + timedelta(hours=1))
    assert tp1.contains(tp2)
    assert not tp2.contains(tp1)

    # if datetime is contained in period
    assert now in tp1
    assert now in tp2

    # __contains__  operator overloading
    assert tp2 in tp1
    assert tp1 not in tp2

    with pytest.raises(TypeError):
        assert 0 in tp1


def test_overlaps():
    now = datetime.now()
    # If periods are just "touching", they should not count as overlap
    tp1 = Timeslot(now - timedelta(hours=1), now)
    tp2 = Timeslot(now, now + timedelta(hours=1))
    assert not tp1.overlaps(tp2)
    assert not tp2.overlaps(tp1)

    # If outer contains inner, or vice versa, they overlap
    tp1 = Timeslot(now, now + timedelta(hours=1))
    tp2 = Timeslot(now - timedelta(hours=1), now + timedelta(hours=2))
    assert tp1.overlaps(tp2)
    assert tp2.overlaps(tp1)

    # If start/end is contained in the other event, they overlap
    tp1 = Timeslot(now, now + timedelta(hours=2))
    tp2 = Timeslot(now - timedelta(hours=1), now + timedelta(hours=1))
    assert tp1.overlaps(tp2)
    assert tp2.overlaps(tp1)


def test_adjacent():
    now = datetime.now()
    tp1 = Timeslot(now - timedelta(hours=1), now)
    tp2 = Timeslot(now, now + timedelta(hours=1))
    assert tp1.adjacent(tp2)
    assert tp2.adjacent(tp1)


def test_union():
    now = datetime.now()

    # adjacent but not overlapping
    tp1 = Timeslot(now - timedelta(hours=1), now)
    tp2 = Timeslot(now, now + timedelta(hours=1))
    tp_union = tp1.union(tp2)
    assert tp1 in tp_union
    assert tp2 in tp_union

    # union with self
    tp_union = tp1.union(tp1)
    assert tp1 == tp_union

    # overlapping
    tp1 = Timeslot(now - timedelta(hours=1), now + timedelta(minutes=30))
    tp2 = Timeslot(now, now + timedelta(hours=1))
    tp_union = tp1.union(tp2)
    assert tp1 in tp_union
    assert tp2 in tp_union

    # tp2 contained in tp1
    tp1 = Timeslot(now - timedelta(minutes=30), now + timedelta(minutes=30))
    tp2 = Timeslot(now, now + timedelta(minutes=10))
    tp_union = tp1.union(tp2)
    assert tp1 in tp_union
    assert tp2 in tp_union
    assert tp1 == tp_union


def test_subtractions_no_overlap():
    # adjacent but not overlapping
    tp1 = Timeslot(datetime(2021, 6, 1, 12), datetime(2021, 6, 1, 14))
    tp2 = Timeslot(datetime(2021, 6, 1, 14), datetime(2021, 6, 1, 16))
    tp_sub = tp2.sub(tp1)
    assert len(tp_sub) == 1
    assert tp_sub[0].start == datetime(2021, 6, 1, 14)
    assert tp_sub[0].end == datetime(2021, 6, 1, 16)


def test_subtractions_overlap_begin():
    # overlapping in the beginning
    tp1 = Timeslot(datetime(2021, 6, 1, 12), datetime(2021, 6, 1, 15))
    tp2 = Timeslot(datetime(2021, 6, 1, 14), datetime(2021, 6, 1, 16))
    tp_sub = tp2.sub(tp1)
    assert len(tp_sub) == 1
    assert tp_sub[0].start == datetime(2021, 6, 1, 15)
    assert tp_sub[0].end == datetime(2021, 6, 1, 16)


def test_subtractions_overlap_end():
    # overlapping in the ending
    tp1 = Timeslot(datetime(2021, 6, 1, 15), datetime(2021, 6, 1, 17))
    tp2 = Timeslot(datetime(2021, 6, 1, 14), datetime(2021, 6, 1, 16))
    tp_sub = tp2.sub(tp1)
    assert len(tp_sub) == 1
    assert tp_sub[0].start == datetime(2021, 6, 1, 14)
    assert tp_sub[0].end == datetime(2021, 6, 1, 15)


def test_subtractions_subslot():
    # tp1 contained in tp2
    tp1 = Timeslot(datetime(2021, 6, 1, 12), datetime(2021, 6, 1, 15))
    tp2 = Timeslot(datetime(2021, 6, 1, 11), datetime(2021, 6, 1, 16))
    tp_sub = tp2.sub(tp1)
    assert len(tp_sub) == 2
    assert tp_sub[0].start == datetime(2021, 6, 1, 11)
    assert tp_sub[0].end == datetime(2021, 6, 1, 12)
    assert tp_sub[1].start == datetime(2021, 6, 1, 15)
    assert tp_sub[1].end == datetime(2021, 6, 1, 16)


def test_subtractions_wrapped():
    # tp1 wraps t2
    tp1 = Timeslot(datetime(2021, 6, 1, 11), datetime(2021, 6, 1, 17))
    tp2 = Timeslot(datetime(2021, 6, 1, 12), datetime(2021, 6, 1, 16))
    tp_sub = tp2.sub(tp1)
    assert len(tp_sub) == 0


def test_subtractions_matches():
    # tp1 matches t2
    tp1 = Timeslot(datetime(2021, 6, 1, 11), datetime(2021, 6, 1, 16))
    tp2 = Timeslot(datetime(2021, 6, 1, 11), datetime(2021, 6, 1, 16))
    tp_sub = tp2.sub(tp1)
    assert len(tp_sub) == 0
