import asyncio
import json
import os
import shutil
import socket
import typing as t
from pathlib import Path

import pytest
from ansible_runner import Runner, RunnerConfig
from nats import NATS
from nats.aio.msg import Msg

from ansible_runner_nats.tools import run_playbook

from natsd import NATSD

PRIVATE_DATA_DIR = Path(__file__).parent / "data"
HOSTNAME = socket.gethostname()


@pytest.mark.asyncio
async def test_run_without_plugin(nats_server: NATSD) -> None:
    """Run a playbook and expect plugin to be disabled."""

    events: t.List[t.Dict[str, t.Any]] = []
    status: t.List[t.Dict[str, t.Any]] = []

    async def events_cb(msg: Msg) -> None:
        nonlocal events
        events.append(json.loads(msg.data))

    async def status_cb(msg: Msg) -> None:
        nonlocal status
        status.append(json.loads(msg.data))

    nc = NATS()
    await nc.connect()

    async with nc:

        # Subscribe to NATS subject
        await nc.subscribe("pub.ansible.runner.*.*.status", cb=status_cb)
        await nc.subscribe("pub.ansible.runner.*.*.events", cb=events_cb)

        # Cleanup before starting test
        if PRIVATE_DATA_DIR.joinpath("artifacts").exists():
            shutil.rmtree(PRIVATE_DATA_DIR / "artifacts")

        # Create runner config
        rc = RunnerConfig(
            private_data_dir=PRIVATE_DATA_DIR.resolve(True).as_posix(),
            playbook="playbook.yml",
        )

        await asyncio.get_running_loop().run_in_executor(None, run_playbook, rc)
        await asyncio.sleep(0.1)
        assert len(status) == 0
        assert len(events) == 0


@pytest.mark.asyncio
async def test_run_with_plugin(nats_server: NATSD) -> None:
    """Run a playbook and expect plugin to be enabled (messages are published on NATS)."""

    events: t.List[t.Dict[str, t.Any]] = []
    status: t.List[t.Dict[str, t.Any]] = []

    async def events_cb(msg: Msg) -> None:
        nonlocal events
        events.append(json.loads(msg.data))

    async def status_cb(msg: Msg) -> None:
        nonlocal status
        status.append(json.loads(msg.data))

    nc = NATS()
    await nc.connect()

    async with nc:

        # Subscribe to NATS subject
        await nc.subscribe("pub.ansible.runner.test.*.status", cb=status_cb)
        await nc.subscribe("pub.ansible.runner.test.*.events", cb=events_cb)

        # Cleanup before starting test
        if PRIVATE_DATA_DIR.joinpath("artifacts").exists():
            shutil.rmtree(PRIVATE_DATA_DIR / "artifacts")

        # Create runner config
        rc = RunnerConfig(
            private_data_dir=PRIVATE_DATA_DIR.resolve(True).as_posix(),
            playbook="playbook.yml",
        )

        loop = asyncio.get_running_loop()
        status_str, status_code = await loop.run_in_executor(
            None, run_playbook, rc, "test"
        )
        await asyncio.sleep(0.1)
        assert status_str == "successful"
        assert status_code == 0
        assert len(status) == 3
        assert len(events) == 0
        expectations = [
            {"status": "starting"},
            {"status": "running"},
            {"status": "successful"},
        ]
        for idx, received in enumerate(status):
            for key, value in expectations[idx].items():
                assert received[key] == value


@pytest.mark.asyncio
async def test_run_with_plugin_from_env(nats_server: NATSD) -> None:
    """Run a playbook and expect plugin to be enabled (messages are published on NATS)."""

    events: t.List[t.Dict[str, t.Any]] = []
    status: t.List[t.Dict[str, t.Any]] = []

    async def events_cb(msg: Msg) -> None:
        nonlocal events
        events.append(json.loads(msg.data))

    async def status_cb(msg: Msg) -> None:
        nonlocal status
        status.append(json.loads(msg.data))

    nc = NATS()
    await nc.connect()

    async with nc:

        # Subscribe to NATS subject
        await nc.subscribe("pub.ansible.runner.test.*.status", cb=status_cb)
        await nc.subscribe("pub.ansible.runner.test.*.events", cb=events_cb)

        # Cleanup before starting test
        if PRIVATE_DATA_DIR.joinpath("artifacts").exists():
            shutil.rmtree(PRIVATE_DATA_DIR / "artifacts")

        # Create runner config
        rc = RunnerConfig(
            private_data_dir=PRIVATE_DATA_DIR.resolve(True).as_posix(),
            playbook="playbook.yml",
        )
        rc.prepare()
        runner = Runner(rc)

        os.environ["RUNNER_NATS_SUBJECT_ID"] = "test"

        try:

            loop = asyncio.get_running_loop()
            status_str, status_code = await loop.run_in_executor(
                None,
                runner.run,
            )
            await asyncio.sleep(0.1)
            assert status_str == "successful"
            assert status_code == 0
            assert len(status) == 3
            assert len(events) == 0
            expectations = [
                {"status": "starting"},
                {"status": "running"},
                {"status": "successful"},
            ]
            for idx, received in enumerate(status):
                for key, value in expectations[idx].items():
                    assert received[key] == value
        finally:
            os.environ.pop("RUNNER_NATS_SUBJECT_ID")
