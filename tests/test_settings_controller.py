import pytest

from undead_idler.settings_controller import InvalidInterval, RuntimeSettings


def test_runtime_settings_start_with_five_minute_default():
    settings = RuntimeSettings()

    assert settings.interval_minutes == 5


@pytest.mark.parametrize("interval", [1, 5, 10])
def test_runtime_settings_accept_supported_whole_minutes(interval):
    settings = RuntimeSettings()

    settings.set_interval(interval)

    assert settings.interval_minutes == interval


@pytest.mark.parametrize("interval", [0, 11, -1, 5.5, "5", True, False])
def test_runtime_settings_reject_invalid_intervals(interval):
    settings = RuntimeSettings()

    with pytest.raises(InvalidInterval):
        settings.set_interval(interval)

    assert settings.interval_minutes == 5


def test_new_runtime_settings_do_not_inherit_prior_session_value():
    first_session = RuntimeSettings()
    first_session.set_interval(8)

    second_session = RuntimeSettings()

    assert second_session.interval_minutes == 5

