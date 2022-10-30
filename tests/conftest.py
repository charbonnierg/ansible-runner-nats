import typing as t
import pytest

from natsd import NATSD, start_natsd


@pytest.fixture
def nats_server() -> t.Iterator[NATSD]:
    server_pool = []
    server = NATSD(port=4222)
    server_pool.append(server)
    for natsd in server_pool:
        start_natsd(natsd)

    try:
        yield natsd
    finally:
        for natsd in server_pool:
            natsd.stop()
