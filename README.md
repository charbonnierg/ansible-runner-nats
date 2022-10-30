Ansible Runner NATS Event Emitter
=================================

This project is a plugin for [Ansible Runner](https://github.com/ansible/ansible-runner) that allows emitting Ansible status and events to NATS in the form of published messages. This can allow `Runner` to notify other systems as Ansible jobs are run and to deliver key events to that system if it's interested.

For more details and the latest documentation see: https://ansible-runner.readthedocs.io/en/latest

## Configuring the emitter

### Default behaviour

By default the emitter is disabled.

### Enabling the emitter

In order to enable the emitter, subject ID must be configured either as `nats_subject_id` variable or as an environment variable:

- `RUNNER_NATS_SUBJECT_ID`: Subject ID

When subject ID is configured, messages are published to the following subjects:

- `pub.ansible.runner.{subject_id}.{runner_ident}.event`: message contains an event

- `pub.ansible.runner.{subject_id}.{runner_ident}.status`: message contains a status update

> `runner_ident` is an auto-generated UUID assigned to each runner instance.

> Special case: if `RUNNER_NATS_SUBJECT_ID` is set to `hostname`, then hostname read using `socket.gethostname()` is used as subject id.


### Configuring headers

Headers can be configured to be sent with each message.

They can be provided as comma separated list of keyvalues (using `=`).

Example: `RUNNER_NATS_HEADERS="producer=ansible-runner,foo=bar"`

### Configuring NATS client

NATS client options can be provided as `nats_options` settings in the runner config settings.

#### Configuring client authentication


The following environment variables can be set to authenticate the client:

- `RUNNER_NATS_USERNAME`: user name
- `RUNNER_NATS_PASSWORD`: user password
- `RUNNER_NATS_TOKEN`: connection token
- `RUNNER_NATS_USER_CREDENTIALS`: user credentials
- `RUNNER_NATS_NKEYS_SEED`: user nkey seed

#### Configuring servers


- `RUNNER_NATS_SERVERS`: comma separated list of NATS server URLs.

#### Advanced configuration

- `RUNNER_NATS_CLIENT_NAME`: client name
- `RUNNER_NATS_CLIENT_VERBOSE`: enable verbose mode when value is `true`, `yes`, `y`, `1` or `on`.
- `RUNNER_NATS_ALLOW_RECONNECT`: allow reconnect when value is `true`, `yes`, `y`, `1` or `on`.
- `RUNNER_NATS_CONNECT_TIMEOUT`: connection timeout in seconds
- `RUNNER_NATS_RECONNECT_TIME_WAIT`: time to wait before reconnecting
- `RUNNER_NATS_MAX_RECONNECT_ATTEMPTS`:  maximum number of reconnect attempts
- `RUNNER_NATS_PING_INTERVAL`: interval between system pings
- `RUNNER_MAX_OUTSTANDING_PINGS`: maximum number of outstanding ping before considering connection stale
- `RUNNER_NATS_FLUSHER_QUEUE_SIZE`: maximum size of flusher queue
