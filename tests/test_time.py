from freezegun import freeze_time
import datetime
from twitter import in_previous_24h

@freeze_time("2012-01-14 03:21:34")
def test_now():
    assert in_previous_24h("2012-01-14 03:21:34")

@freeze_time("2012-01-14 03:21:34")
def test_hour_ago():
    assert in_previous_24h("2012-01-14 02:21:34")

@freeze_time("2012-01-14 03:21:34")
def test_yesterday():
    assert not in_previous_24h("2012-01-14 03:21:34")

@freeze_time("2012-01-14 03:21:34")
def test_now_timestamp():
    assert in_previous_24h(datetime.now().timestamp())