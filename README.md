# QueueProof — support routing with a visible review boundary

A support automation agency needs to sort incoming requests and catch questionable routes before a help-desk handoff. QueueProof suggests one of 77 banking support intents, shows competing candidates, keeps low-margin messages for a person, and exports the accepted or manually corrected suggestions. It runs on real public BANKING77 messages rather than made-up happy-path tickets.

**Deployment status:** working local static demo; public URL will be added only after deployment and a cold check. No live-host claim is made here. Default hosting is a $0 GitHub Pages engineering demonstration. No customer production integration is included.

## Try it in 60 seconds

Python 3.12+ is sufficient; no dependency installation or internet is needed for the committed sample and pretrained browser model.

```sh
python run.py --reset
```

Open `http://127.0.0.1:8763/`. Click **Load real message batch**, inspect the **Needs review** tab, select a route after reading the original message, then download suggested routes. Every page load and **Reset workspace** clears local session state. There is no login, database, key or saved customer data. Model and source sample are served locally; initial model download is about 6.84 MB on the published site.

**No API key or environment variable is required for the default demo.** No paid API, hidden free-trial dependency or optional credential is used. There is consequently no API-key acquisition step. `.env` files are ignored and must never be committed.

## Measured results, not customer savings

Measured 3 October 2026. Training-only keyword baseline selects five distinctive unigram rules per intent from development data (minimum three occurrences), summing matches; ties fall back to alphabetical intent order. The learned model is word/bigram TF-IDF plus a linear SVM. No LLM is involved. Both use the same held-out input text. This is a narrow keyword baseline, not a comparison against modern language models or expert human routing.

| Evaluation | Official test | Normalized-deduplicated test |
|---|---:|---:|
| Queries | 3,080 | 3,055 |
| Keyword baseline accuracy | 47.37% | 47.27% |
| Learned model accuracy, all messages | 88.21% | 88.12% |
| Model macro-F1 | 0.8821 | 0.8811 |
| Suggestions meeting margin policy | 2,591 / 3,080 (84.12%) | 2,566 / 3,055 (83.99%) |
| Wrong accepted suggestions | **122 / 2,591 (4.71%)** | **122 / 2,566 (4.75%)** |
| Sent to review | 489 / 3,080 | 489 / 3,055 |

On the cleaned test, accuracy improves by **40.85 percentage points** over this frozen baseline. The policy still wrongly accepts 122 suggestions: it is not safe unattended routing. Threshold **0.3344583** was the smallest of 101 validation-gap quantile candidates achieving at least 95% correct accepted suggestions and at least 100 accepted validation rows. Raw SVM scores and top-two gaps are **uncalibrated decision scores, not probabilities**.

Warm Python inference (vectorization plus decision function), first 200 official test queries: **p50 1.27 ms / p95 2.39 ms** on this build machine. This is a local observational timing, not network latency, a service SLA or customer labor savings. A 40-message UI batch takes milliseconds after the model loads; speed depends on the browser/device. Human sorting time, customer losses and time saved have not been measured. [Full results and per-class metrics](evaluation/results.json); per-class numeric keys map to the ordered class list in `public/model.json`.

## A failure is part of the demonstration

Real held-out `banking77-test-2`: **“I ordered a card but it has not arrived. Help please!”** The model's first suggestion is `transfer_not_received_by_recipient`; the correct benchmark label is `card_arrival`, its second candidate. Its gap is 0.085, below the threshold, so it goes to review. The UI does not load its correct label: the operator reads the source and chooses the appropriate intent. The capture script selects `card_arrival` to show a human correction and exports that choice; benchmark metrics never include this manual correction.

The other limitation is more serious: the separately authored OOD fixture “Please book a dentist appointment tomorrow” is wrongly accepted as `cancel_transfer` (gap 0.670). This four-example behavior check is synthetic and separate from real-data accuracy. Margin review cannot certify domain membership. Apply this system to a buyer's data only after representative labelled evaluation and an agreed routing risk policy.

## Reproduce and inspect

```sh
python -m pip install -r requirements.txt
python scripts/acquire.py
python scripts/train_evaluate.py
python -m unittest discover -s tests -v
python -m playwright install chromium
python scripts/capture.py
```

Acquisition uses immutable publisher URLs and refuses changed SHA-256 values. Full source CSVs are ignored; the offline sample, derived model and metrics are committed. Training uses a grouped 8,002/2,001 development/validation split, seed 42. Labels are used only for training/evaluation, never inference. The model and threshold freeze before official test scoring. Rerunning may change machine timing; numerical metrics should reproduce under the pinned dependency versions. See [DATA.md](DATA.md) for rights, attribution, split contamination, provenance and preprocessing.

The default capture script starts its own local server, drives a 1920×1080 headless Chromium browser through input, inference, review, correction, export and reset, and checks browser/Python score parity on 12 held-out inputs. Use `python scripts/capture.py --url https://YOUR-ACTUAL-DEMO-URL/` to capture the deployed site. Screens and report go to ignored `capture/`. The verified local run had **1.17e-9** maximum score difference and zero browser errors. CI repeats unit contracts and browser flow; it is configured but no hosted CI success is claimed until GitHub actually runs it.

To stage hosting: `python scripts/stage_site.py`; deploy **site/**. Pages workflow stages only the app, input-only sample, model, measured results and licence files. Audit labels/training CSVs are excluded. It is a fixed public-data demonstration, not a commercial SaaS, checkout or customer-data hosting service.

## What a buyer can purchase

Start with a **$100 labelled-message routing audit** (≤100 permission-cleared messages, one taxonomy, 3 days, one revision). A **$300** classifier/evaluation/export package covers one agreed taxonomy (6 days, two revisions); **$500** adds a review UI and handover (10 days, two revisions). These are proposed prices to test, not verified revenue or promises about benchmark-to-customer transfer. Production help-desk integration is a separate **$1,500–4,500** scope after paid discovery, authentication/rate-limit design, held-out acceptance criteria and annotation needs are agreed. Vendor administration, SLA workflows and production Zendesk experience are not proven by this demo.

Limitations: English banking domain only; curated benchmark with incomplete public collection-chain details; no calibrated probabilities, OOD detector, multilingual claim, LLM answers, bank account actions, customer ROI or real vendor integration. Batch max 100 messages, max 2,000 characters each. CSV formula-like values are escaped; browser text is rendered as text, not HTML. No form input leaves the browser or persists after reset.
