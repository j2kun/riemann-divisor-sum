'''A script that checks for docker failures, alerting via email if a container fails.'''

from dotenv import load_dotenv
from shutil import which
from typing import Callable
import os
import subprocess
import time
import traceback


def run(sendmail: Callable[[str], None],
        subprocess_runner: Callable[[str], str],
        success_sleep_seconds: int = 5*60,
        failure_sleep_seconds: int = 60*60,
        should_stop: Callable[[], bool] = lambda: False) -> None:
    while True:
        print("Checking docker...")
        output = subprocess_runner(
            'docker ps -a --format="{{.Image}}" --filter="status=exited"')
        if output:
            print(f"Dead containers:\n {output}")
            docker_ps = subprocess_runner('docker ps -a')
            hostname = subprocess_runner('hostname')
            domainname = subprocess_runner('dnsdomainname')
            sendmail(
                f"Detected docker failures on {hostname}.{domainname}\n\n{docker_ps}")
            time.sleep(failure_sleep_seconds)
        else:
            print("No dead containers. Sleeping.")
            time.sleep(success_sleep_seconds)

        if should_stop():
            return


if __name__ == "__main__":
    if which("ssmtp") is None:
        raise Exception("Must install ssmtp: apt-get install ssmtp")

    load_dotenv()

    def subprocess_runner(program: str) -> str:
        print(f"Running: {program}")
        return subprocess.check_output([program], shell=True).decode("utf-8") 

    def sendmail(message: str) -> None:
        email_dest = os.environ['GMAIL_APP_USER']
        email_pass = os.environ['GMAIL_APP_PASS']
        print(f"Sending message to {email_dest}: {message}")
        subprocess.check_output(["ssmtp", "-ap", email_pass, email_dest], text=True, input=message)

    try:
        run(sendmail, subprocess_runner)
    except KeyboardInterrupt:
        # Ctrl-C exits with no alert raised
        pass
    except Exception as e:
        tb = traceback.format_exc()
        # monitor program failed erroneously
        sendmail(
            f"monitor_docker failed with exception: {e}\n\nTraceback: {tb}")
