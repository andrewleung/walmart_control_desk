# Walmart Inventory & Commitment Control — Synthetic Demo

> **Synthetic demonstration data — not for operational use**

A local, single-user Django MVP for Jessica. It turns recurring Walmart, warehouse,
shipment, factory, and review files into a dated reconciliation cycle with blocking
exceptions and an exportable inventory-and-commitment schedule.

The Render deployment is a public, read-only demonstration containing only the
made-up complete-workflow cycle. Operational source files and the real partial-data
trial are excluded from the deployment repository.

## Start the application

```bash
cd walmart-control
source .venv/bin/activate
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000`.

For a demonstration, use the one-command launcher:

```bash
./run_demo.sh
```

It applies any pending database updates, loads both the real partial-data trial and
the separate synthetic complete-workflow demonstration, and starts the application
at `http://127.0.0.1:8000`.

To prepare and present only one demo:

```bash
./run_partial_demo.sh
./run_synthetic_demo.sh
```

Use `run_partial_demo.sh` with `demo_data/PARTIAL_DATA_DEMO_TALKSCRIPT.md`.
Use `run_synthetic_demo.sh` with `demo_data/SYNTHETIC_DEMO_TALKSCRIPT.md`.

## Load the demonstration cycle

The seed command uses the existing files in `../walmart-export/`:

```bash
python manage.py seed_trial
```

It intentionally demonstrates a partial run. Missing critical supply and commitment
packages remain visible and prevent a final supply conclusion.

## MVP workflow

1. Create a control cycle and cutoff date.
2. Upload the nine input packages.
3. Review file processing and field coverage.
4. Run reconciliation.
5. Resolve blocking exceptions.
6. Record Jessica's status and notes per item.
7. Export the Excel schedule or print the management report to PDF.

Uploaded data stays in `data/` on the local computer. No external service is used.

## Synthetic complete-workflow demonstration

The nine clearly labeled made-up source files are in `demo_data/synthetic/`. They
populate a separate cycle with three illustrative outcomes: covered surplus,
shortage, and inbound arriving after the applicable MABD. The cycle and every
export are labeled as synthetic and must not be used operationally.

Jessica's presentation notes are in `demo_data/SYNTHETIC_DEMO_TALKSCRIPT.md`.

## Render synthetic demonstration

`render.yaml` defines a free, resettable, read-only deployment. The hosted
configuration displays only the synthetic cycle, blocks uploads and changes,
and recreates the synthetic database whenever the service restarts.

Create a repository containing this `walmart-control` directory, connect that
repository as a Render Blueprint, and apply the included `render.yaml`. Do not
add `data/`, `walmart-export/` or other operational source folders to the
deployment repository.
