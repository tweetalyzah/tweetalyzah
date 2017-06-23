from freezegun import freeze_time
from datetime import datetime
from ..twitter import in_previous_24h


@freeze_time("2015-06-19 12:25:37")
def test_now():
    assert in_previous_24h("Fri Jun 19 12:25:37 +0000 2015")


@freeze_time("2015-06-19 12:25:37")
def test_hour_ago():
    assert in_previous_24h("Fri Jun 19 11:25:37 +0000 2015")


@freeze_time("2015-06-19 12:25:37")
def test_yesterday():
    assert not in_previous_24h("Thu Jun 18 10:25:36 +0000 2015")

