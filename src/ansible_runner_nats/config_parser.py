import logging
import os
import socket
import typing as t

if t.TYPE_CHECKING:
    from ansible_runner.config.runner import RunnerConfig


logger = logging.getLogger("ansible-runner.nats")


def parse_nats_options(runner_config: "RunnerConfig") -> t.Dict[str, t.Any]:
    """Parse NATS options from environment"""
    environ = os.environ
    options = dict(
        servers=[server.strip() for server in environ["RUNNER_NATS_SERVERS"].split(",")]
        if "RUNNER_NATS_SERVERS" in environ
        else None,
        name=environ.get("RUNNER_NATS_CLIENT_NAME", None),
        verbose=environ["RUNNER_NATS_CLIENT_VERBOSE"].lower()
        in ["true", "yes", "1", "y", "on"]
        if "RUNNER_NATS_CLIENT_VERBOSE" in environ
        else None,
        allow_reconnect=environ["RUNNER_NATS_ALLOW_RECONNECT"].lower()
        in ["true", "yes", "1", "y", "on"]
        if "RUNNER_NATS_ALLOW_RECONNECT" in environ
        else None,
        connect_timeout=float(environ["RUNNER_NATS_CONNECT_TIMEOUT"])
        if "RUNNER_NATS_CONNECT_TIMEOUT" in environ
        else None,
        reconnect_time_wait=float(environ["RUNNER_NATS_RECONNECT_TIME_WAIT"])
        if "RUNNER_NATS_RECONNECT_TIME_WAIT" in environ
        else None,
        max_reconnect_attempts=int(environ["RUNNER_NATS_MAX_RECONNECT_ATTEMPTS"])
        if "RUNNER_NATS_MAX_RECONNECT_ATTEMPTS" in environ
        else None,
        ping_interval=float(environ["RUNNER_NATS_PING_INTERVAL"])
        if "RUNNER_NATS_PING_INTERVAL" in environ
        else None,
        max_outstanding_pings=int(environ["RUNNER_MAX_OUTSTANDING_PINGS"])
        if "RUNNER_MAX_OUTSTANDING_PINGS" in environ
        else None,
        flusher_queue_size=int(environ["RUNNER_NATS_FLUSHER_QUEUE_SIZE"])
        if "RUNNER_NATS_FLUSHER_QUEUE_SIZE" in environ
        else None,
        user=environ.get("RUNNER_NATS_USERNAME", None),
        password=environ.get("RUNNER_NATS_PASSWORD", None),
        token=environ.get("RUNNER_NATS_TOKEN", None),
        user_credentials=environ.get("RUNNER_NATS_USER_CREDENTIALS", None),
        nkeys_seed=environ.get("RUNNER_NATS_NKEYS_SEED", None),
        pending_size=int(environ["RUNNER_NATS_PENDING_SIZE"])
        if "RUNNER_NATS_PENDING_SIZE" in environ
        else None,
        flush_timeout=float(environ["RUNNER_NATS_FLUSH_TIMEOUT"])
        if "RUNNER_NATS_FLUSH_TIMEOUT" in environ
        else None,
    )
    extras = {key: value for key, value in options.items() if value is not None}
    nats_options: t.Dict[str, t.Any] = runner_config.settings.get("nats_options", {})
    return {**nats_options, **extras}


def parse_subject_id(runner_config: "RunnerConfig") -> t.Optional[str]:
    subject_id = os.environ.get("RUNNER_NATS_SUBJECT_ID", None)
    if subject_id == "hostname":
        return socket.gethostname().replace(".", "-")
    elif subject_id:
        return subject_id
    else:
        return t.cast(
            t.Optional[str], runner_config.settings.get("nats_subject_id", None)
        )


def parse_headers(runner_config: "RunnerConfig") -> t.Dict[str, str]:
    headers = os.environ.get("RUNNER_NATS_HEADERS", "")
    if not headers:
        return {}
    keyvalues = [tuple(keyvalue.strip().split("=")) for keyvalue in headers.split(",")]
    try:
        extra_headers: t.Dict[str, str] = dict(keyvalues)  # type: ignore[arg-type]
    except ValueError as exc:
        # Invalid headers do not lead to program crash
        # Error is only logged
        logger.error("Invalid headers", exc_info=exc)
    nats_headers: t.Dict[str, str] = runner_config.settings.get("nats_headers", {})
    return {**nats_headers, **extra_headers}
