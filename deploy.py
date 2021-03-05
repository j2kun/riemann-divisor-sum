from dataclasses import dataclass
from dotenv import load_dotenv
import os
import paramiko


def connect(host: str) -> paramiko.SSHClient:
    ssh = paramiko.SSHClient()
    k = paramiko.RSAKey.from_private_key_file(os.environ['SSH_KEY_PATH'])
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username='ubuntu', pkey=k)
    return ssh


def run(client, command):
    print(f'[{w.envvar}] Running: {cmd}')
    stdin, stdout, stderr = client.exec_command(cmd)
    print(stdout.read().decode('utf-8'))
    print(stderr.read().decode('utf-8'))


@dataclass(frozen=True)
class Worker:
    envvar: str

    # used for both container name and Dockerfile name
    container_name: str

    docker_run_args: str


if __name__ == "__main__":
    choice = input("About to deploy. Are you sure? [y/N] ")
    if choice.lower()[0] == 'y':
        load_dotenv()
        pg_host = os.environ['EC2_DIVISORDB']

        # topologically sorted in dependency order,
        # first entry has no dependencies
        workers = [
            Worker(
                envvar='EC2_DIVISORDB',
                container_name='divisordb',
                docker_run_args='-p 5432:5432',
            ),
            Worker(
                envvar='EC2_GENERATOR',
                container_name='generate',
                docker_run_args=f'--env PGHOST="{pg_host}"',
            ),
            Worker(
                envvar='EC2_CLEANUP',
                container_name='cleanup',
                docker_run_args=f'--env PGHOST="{pg_host}"',
            ),
            Worker(
                envvar='EC2_PROCESSOR1',
                container_name='process',
                docker_run_args=f'--env PGHOST="{pg_host}"',
            ),
            Worker(
                envvar='EC2_PROCESSOR2',
                container_name='process',
                docker_run_args=f'--env PGHOST="{pg_host}"',
            ),
        ]

        instances = {}

        for w in workers:
            host = os.environ[w.envvar]
            print(f"Connecting to {w.envvar}={host}")
            instances[w] = connect(host)

        # stop containers, remove old images, and build new images
        for w in reversed(workers):
           client = instances[w]
           cmd = f'docker stop {w.container_name}; docker image prune -a -f'
           run(client, cmd)

           cmd = (
               f'cd riemann-divisor-sum && '
               f'git reset --hard origin/main && git pull && '
               f'docker build -t {w.container_name} -f docker/{w.container_name}.Dockerfile .'
           )
           run(client, cmd)

        for w in workers:
           client = instances[w]
           cmd = (
               f'docker run -d --name {w.container_name} {w.docker_run_args} {w.container_name}:latest'
               f' && sleep 5'
           )
           run(client, cmd)
