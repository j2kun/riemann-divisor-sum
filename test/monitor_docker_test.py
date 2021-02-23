from multiprocessing import Process
import pytest
import time
from pytest_cov.embed import cleanup_on_sigterm

from alerts import monitor_docker


cleanup_on_sigterm()


class FakeCallable:
    def __init__(self):
        self.call_count = 0

    def __str__(self):
        return f"FakeCallable(call_count={self.call_count})"


def make_fake_subprocess_runner(fn):
    class FakeSubprocessRunner(FakeCallable):
        def __call__(self, program: str):
            self.call_count += 1
            return fn(program)
    return FakeSubprocessRunner()


class FakeSendmail(FakeCallable):
    def __call__(self, message: str):
        self.call_count += 1


def test_no_alert_on_success():
    def runner(program):
        if program.startswith('docker'):
            return ""
        else:
            raise ValueError("Test should fail!")

    sendmail = FakeSendmail()
    subprocess_runner = make_fake_subprocess_runner(runner)

    def run_monitor():
        monitor_docker.run(
            sendmail, 
            subprocess_runner,
            success_sleep_seconds=1,
            failure_sleep_seconds=1,
            should_stop=lambda: subprocess_runner.call_count == 5
        )

    run_monitor()
    assert sendmail.call_count == 0
    assert subprocess_runner.call_count == 5
