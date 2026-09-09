from undead_idler.app import main


def test_application_event_loop_exits_cleanly():
    assert main([]) == 0

