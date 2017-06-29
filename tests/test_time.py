'''Test file to check if in_previous_24h function works correctly'''


from freezegun import freeze_time
from ..twitter import in_previous_24h


@freeze_time("2015-06-19 12:25:37")
def test_now():
    '''Test function to check if in_previous_24h
     returns True for current time'''
    assert in_previous_24h("Fri Jun 19 12:25:37 +0000 2015")


@freeze_time("2015-06-19 12:25:37")
def test_hour_ago():
    '''Test function to check if in_previous_24h
     works for dates around hour before current time'''
    assert in_previous_24h("Fri Jun 19 11:25:37 +0000 2015")
    assert in_previous_24h("Fri Jun 19 11:40:37 +0000 2015")
    assert in_previous_24h("Fri Jun 19 12:25:00 +0000 2015")
    assert in_previous_24h("Fri Jun 19 11:25:36 +0000 2015")


@freeze_time("2015-06-19 12:25:37")
def test_yesterday():
    '''Test function to check if in_previous_24h
     works for dates from a day before current time'''
    assert not in_previous_24h("Thu Jun 18 08:25:36 +0000 2015")
    assert not in_previous_24h("Thu Jun 18 10:25:36 +0000 2015")
    assert not in_previous_24h("Thu Jun 18 10:25:37 +0000 2015")
