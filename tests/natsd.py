# type: ignore
import http.client
import time
import os
import signal
import subprocess
import tempfile
from pathlib import Path


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_BIN_DIR_NAME = "nats-server"


def start_natsd(natsd: "NATSD"):
    natsd.start()

    endpoint = f"127.0.0.1:{natsd.http_port}"
    retries = 0
    while True:
        if retries > 100:
            break

        try:
            httpclient = http.client.HTTPConnection(endpoint, timeout=5)
            httpclient.request("GET", "/varz")
            response = httpclient.getresponse()
            if response.status == 200:
                break
        except ConnectionRefusedError:
            retries += 1
            time.sleep(0.1)


class NATSD:
    def __init__(
        self,
        port=4222,
        user="",
        password="",
        token="",
        timeout=0,
        http_port=8222,
        debug=False,
        config_file=None,
        with_jetstream=None,
    ):
        self.port = port
        self.user = user
        self.password = password
        self.timeout = timeout
        self.http_port = http_port
        self.proc = None
        self.token = token
        self.bin_name = "nats-server"
        self.config_file = config_file
        self.debug = debug or os.environ.get("DEBUG_NATS_TEST") == "true"

        if with_jetstream:
            self.store_dir = tempfile.mkdtemp()

    def start(self):
        # Default path
        if Path(self.bin_name).is_file():
            self.bin_name = Path(self.bin_name).absolute()
        # Path in `../scripts/install_nats.sh`
        elif Path.home().joinpath(SERVER_BIN_DIR_NAME, self.bin_name).is_file():
            self.bin_name = str(
                Path.home().joinpath(SERVER_BIN_DIR_NAME, self.bin_name)
            )
        # This directory contains binary
        elif Path(THIS_DIR).joinpath(self.bin_name).is_file():
            self.bin_name = str(Path(THIS_DIR).joinpath(self.bin_name))

        cmd = [
            self.bin_name,
            "-p",
            "%d" % self.port,
            "-m",
            "%d" % self.http_port,
            "-a",
            "127.0.0.1",
        ]
        if self.user:
            cmd.append("--user")
            cmd.append(self.user)
        if self.password:
            cmd.append("--pass")
            cmd.append(self.password)

        if self.token:
            cmd.append("--auth")
            cmd.append(self.token)

        if self.debug:
            cmd.append("-DV")

        if self.config_file is not None:
            cmd.append("--config")
            cmd.append(self.config_file)

        if self.debug:
            self.proc = subprocess.Popen(cmd)
        else:
            self.proc = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

        if self.debug:
            if self.proc is None:
                print(
                    "[\031[0;33mDEBUG\033[0;0m] Failed to start server listening on port %d started."
                    % self.port
                )
            else:
                print(
                    "[\033[0;33mDEBUG\033[0;0m] Server listening on port %d started."
                    % self.port
                )
        return self.proc

    def stop(self):
        if self.debug:
            print(
                "[\033[0;33mDEBUG\033[0;0m] Server listening on %d will stop."
                % self.port
            )

        if self.debug:
            if self.proc is None:
                print(
                    "[\033[0;31mDEBUG\033[0;0m] Failed terminating server listening on port %d"
                    % self.port
                )

        if self.proc.returncode is not None:
            if self.debug:
                print(
                    "[\033[0;31mDEBUG\033[0;0m] Server listening on port {port} finished running already with exit {ret}".format(
                        port=self.port, ret=self.proc.returncode
                    )
                )
        else:
            os.kill(self.proc.pid, signal.SIGKILL)
            self.proc.wait()
            if self.debug:
                print(
                    "[\033[0;33mDEBUG\033[0;0m] Server listening on %d was stopped."
                    % self.port
                )
