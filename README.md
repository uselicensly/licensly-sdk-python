# Licensly Python SDK

Official Python client for the Licensly Client API. Activate licenses, keep signed leases fresh with heartbeats, and verify Ed25519 envelopes before trusting lease data.

Requires Python 3.10+.

## Install

```bash
pip install licensly
```

## Quick start

```python
from licensly import Client

with Client(
    base_url="https://your-licensly-host.example",
    product_id="prd_…",
    public_key_hex="<product Ed25519 public key>",
) as client:
    activation = client.activate(
        license_key="XXXX-XXXX-XXXX-XXXX",
        device_id="stable-device-fingerprint",  # you choose this; the SDK never collects hardware IDs
    )
    print(activation.lease.license_status)

    session = client.session(activation)
    session.start()   # background heartbeats
    # … your application …
    session.stop()    # ends this client session only; device binding stays until admin reset/release
```

Docs: https://licensly.dev/docs

## Development

```bash
python -m pip install -e ".[dev]"
./scripts/fetch-contract.sh
pytest
```

## Contract pin

This repo commits only `contract.lock.json`. Golden fixtures are fetched and verified into `.contract/`:

```bash
./scripts/fetch-contract.sh
pytest
```

When the published API contract changes, bump `contract.lock.json` to the new `contract_version` and bundle SHA-256, then re-run fetch.
