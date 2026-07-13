# Licensly Python SDK

Official Python client for the Licensly Client API. Activate licenses, keep signed leases fresh with heartbeats, and verify Ed25519 envelopes before trusting lease data.

Requires Python 3.10+.

## Install

```bash
pip install git+https://github.com/uselicensly/licensly-sdk-python.git
```

## Quick start

```python
from licensly import Client

with Client(
    base_url="https://your-licensly-host.example",
    product_id="prd_…",
    public_key_hex="<product Ed25519 public key>",
) as client:
    validation = client.validate(
        license_key="LIC-8F2A-19C4-7B61-D0E3",
        device_id="installation-8f27c1a4",
        app_version="2.3.1",
    )
    print(validation.license_status)  # unsigned, online-only result

    activation = client.activate(
        license_key="LIC-8F2A-19C4-7B61-D0E3",
        device_id="installation-8f27c1a4",  # opaque, stable ID chosen by your app
        app_version="2.3.1",
    )
    print(activation.lease.license_status)

    session = client.session(activation)
    session.start()   # background heartbeats
    # … your application …
    session.stop()    # ends this client session only; device binding stays until admin reset/release
```

Pass `issue_session=True` to `validate` when you need it to return an
`Activation` with a verified signed lease and session token. The default
sessionless result is unsigned and must not be trusted offline.

Docs: https://licensly.dev/docs

## Development

```bash
python -m pip install -e ".[dev]"
pytest
```

## Contract pin

`contract.lock.json` records which Licensly API contract this SDK targets.
Signing golden vectors used by unit tests are vendored under `tests/fixtures/` and must
match the pinned contract version when the lock is bumped.
