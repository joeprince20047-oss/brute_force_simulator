# Architecture Overview

## System Components

```
┌─────────────────────────────────────────────────────┐
│                    main.py (CLI)                    │
│         argparse → Config → BruteForceAttacker      │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │    BruteForceAttacker   │
        │  - Queue management     │
        │  - Thread pool          │
        │  - Response analysis    │
        └──┬──────────┬───────────┘
           │          │
    ┌──────▼──┐  ┌────▼──────┐
    │Wordlist │  │ Reporter  │
    │Loader / │  │ - Logging │
    │BFGen    │  │ - CSV/JSON│
    └─────────┘  └───────────┘
           │
    ┌──────▼──────────────┐
    │  Flask Sandbox      │
    │  (localhost:5000)   │
    │  - /login endpoint  │
    │  - AuthGuard        │
    └─────────────────────┘
```

## Data Flow

1. CLI parses arguments → creates `Config` dataclass
2. `BruteForceAttacker` loads passwords via `WordlistLoader` or `BruteForceGen`
3. Passwords are placed into a thread-safe `Queue`
4. Worker threads dequeue and POST to the Flask target
5. Responses are classified as success / failure / rate-limit
6. `Reporter` logs stats and saves results on completion

## Concurrency Model

- Python `threading.Thread` (not multiprocessing)
- Shared state protected by `threading.Lock` in `Reporter`
- `threading.Event` used to signal found credentials across all threads
- Queue is `daemon=True` so threads die when main thread exits
