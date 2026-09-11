from undead_idler import instance_guard


def test_non_windows_acquisition_returns_a_noop_guard(monkeypatch):
    monkeypatch.setattr(instance_guard, "_running_on_windows", lambda: False)

    guard = instance_guard.acquire_instance("test-name")

    assert guard is not None
    assert guard.acquired is False
    guard.release()


def test_duplicate_mutex_is_closed_and_rejected(monkeypatch):
    close_calls = []

    class FakeFunction:
        def __init__(self, callback):
            self._callback = callback

        def __call__(self, *args):
            return self._callback(*args)

    class FakeKernel32:
        CreateMutexW = FakeFunction(lambda *_args: 123)
        CloseHandle = FakeFunction(lambda handle: close_calls.append(handle) or 1)

    monkeypatch.setattr(instance_guard, "_running_on_windows", lambda: True)
    monkeypatch.setattr(instance_guard.ctypes, "WinDLL", lambda *_args, **_kwargs: FakeKernel32())
    monkeypatch.setattr(instance_guard.ctypes, "get_last_error", lambda: instance_guard.ERROR_ALREADY_EXISTS)

    assert instance_guard.acquire_instance("test-name") is None
    assert close_calls == [123]


def test_owned_guard_releases_only_once():
    close_calls = []
    guard = instance_guard.InstanceGuard(456, close_calls.append)

    assert guard.acquired is True
    guard.release()
    guard.release()

    assert close_calls == [456]


def test_duplicate_launch_exits_before_creating_qt_application(monkeypatch):
    from undead_idler import app

    monkeypatch.setattr(app, "acquire_instance", lambda: None)
    monkeypatch.setattr(
        app,
        "create_application",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("Qt should not start")),
    )

    assert app.main([]) == 0
