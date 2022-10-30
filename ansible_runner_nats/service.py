import asyncio
import json
import logging
import typing as t

from nats import NATS

if t.TYPE_CHECKING:
    import concurrent.futures


logger = logging.getLogger("ansible-runner.nats")


class NATSEmitterService:
    def __init__(self) -> None:
        self.subject_id: str = ""
        self.options: t.Dict[str, t.Any] = {}
        self.headers: t.Dict[str, str] = {}
        self.loop = asyncio.get_event_loop_policy().new_event_loop()
        self.client = NATS()

    def get_subject(self, data: t.Dict[str, t.Any], typ: str) -> str:
        """Get subject to which message will be published"""
        base = "pub.ansible.runner"
        ident: str = data["runner_ident"]
        return f"{base}.{self.subject_id}.{ident}.{typ}"

    async def async_send_data(self, typ: str, data: t.Dict[str, t.Any]) -> None:
        """Send some data on NATS"""
        return await self.client.publish(
            subject=self.get_subject(data, typ),
            payload=json.dumps(data).encode("utf-8"),
            headers=self.headers,
        )

    async def async_send_stop(self) -> None:
        """Send stop command to NATS client"""
        try:
            await self.client.close()
        finally:
            self.loop.stop()

    def send_data(
        self, typ: str, data: t.Dict[str, t.Any]
    ) -> "concurrent.futures.Future[None]":
        """Send data to the emitter. Data is not published yet when this function returns."""
        return asyncio.run_coroutine_threadsafe(
            self.async_send_data(typ, data), self.loop
        )

    def send_stop(self) -> "concurrent.futures.Future[None]":
        """Send a stop command the emitter. Emitter is not stopped yet when this function returns."""
        return asyncio.run_coroutine_threadsafe(self.async_send_stop(), self.loop)

    def mainloop(self) -> None:
        """Main loop of the emitter. This function starts the emitter then waits until a stop is received."""
        asyncio.set_event_loop(self.loop)
        # Pending size can be updated during connection
        self.client._max_pending_size = 1024 * 1024
        self.loop.create_task(self.client.connect(**self.options))
        self.loop.run_forever()
