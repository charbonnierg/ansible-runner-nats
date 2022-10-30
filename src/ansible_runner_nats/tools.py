import typing as t

from ansible_runner import Runner

if t.TYPE_CHECKING:
    from ansible_runner import RunnerConfig


def run_playbook(
    config: "RunnerConfig",
    nats_subject_id: t.Optional[str] = None,
    nats_options: t.Optional[t.Dict[str, t.Any]] = None,
    nats_headers: t.Optional[t.Dict[str, t.Any]] = None,
) -> t.Tuple[t.Union[str, t.Any], t.Union[int, t.Any]]:
    """"""
    config.prepare()

    if nats_options is not None:
        config.settings["nats_options"] = nats_options
    if nats_headers:
        config.settings["nats_headers"] = nats_headers
    if nats_subject_id:
        config.settings["nats_subject_id"] = nats_subject_id
    runner = Runner(config)
    state, status_code = runner.run()
    return str(state), int(status_code)
