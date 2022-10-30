import logging
import threading
import typing as t

if t.TYPE_CHECKING:
    from ansible_runner.config.runner import RunnerConfig

from ansible_runner_nats.config_parser import (
    parse_headers,
    parse_nats_options,
    parse_subject_id,
)
from ansible_runner_nats.service import NATSEmitterService

logger = logging.getLogger("ansible-runner.nats")


service_registry: t.Dict[str, NATSEmitterService] = {}
thread_registry: t.Dict[str, threading.Thread] = {}


def set_configuration(
    ident: str, runner_config: "RunnerConfig"
) -> t.Optional[NATSEmitterService]:
    # Parse subject id
    nats_subject_id = parse_subject_id(runner_config)
    if not nats_subject_id:
        logger.debug("Runner 'nats' plugin skipped")
        return None
    if ident not in service_registry:
        # Create new service
        service = NATSEmitterService()
        service.subject_id = nats_subject_id
        service.headers = parse_headers(runner_config)
        service.options = parse_nats_options(runner_config)
        # Save service
        service_registry[ident] = service
        # Create new thread
        service_thread = threading.Thread(target=service.mainloop)
        service_thread.start()
        # Save thread
        thread_registry[ident] = service_thread
    # Return service
    return service_registry[ident]


def clear_registries() -> None:
    service_registry.clear()
    thread_registry.clear()


def status_handler(runner_config: "RunnerConfig", data: t.Dict[str, t.Any]) -> None:
    # Get runner ident
    ident = data["runner_ident"]
    # First set configuration
    service = set_configuration(ident, runner_config)
    if service is None:
        return
    # Send data to runner service
    service.send_data("status", data)
    # Stop runner service on specific status changes
    if "status" in data and data["status"] in (
        "canceled",
        "successful",
        "timeout",
        "failed",
    ):
        service.send_stop()
        service_registry.pop(ident)
        thread_registry.pop(ident)


def event_handler(runner_config: "RunnerConfig", data: t.Dict[str, t.Any]) -> None:
    # Get runner ident
    ident = data["runner_ident"]
    # First set configuration
    service = set_configuration(ident, runner_config)
    if service is None:
        return
    service.send_data("event", data)
