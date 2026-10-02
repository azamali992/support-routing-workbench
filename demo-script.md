# Timed product walkthrough

Capture: `python scripts/capture.py --url ACTUAL_PUBLIC_URL`. Warm all static assets before recording; start from reset. Do not show a model download spinner mid-story. No seller mic/camera is needed for the product flow. An optional genuine spoken introduction can be recorded separately; never synthesize a seller testimonial or claim trust lift.

| Time | Actual screen/action | Caption / optional voiceover |
|---|---|---|
| 0–7s | Intake, 40-message public source | “Support requests overlap. A wrong route creates another handoff.” |
| 7–17s | Load real batch → actual browser classification | “Sort real BANKING77 messages across 77 banking support intents.” |
| 17–28s | Result / clean benchmark | “88.12% accuracy versus 47.27% for a training-only keyword baseline, on 3,055 clean held-out queries.” |
| 28–39s | Needs review → test-2 original text and scores | “The first candidate is wrong here. A small candidate gap sends it to review.” |
| 39–48s | Human selects card arrival, confirms | “Read the source, compare candidates, then choose the intended route.” |
| 48–56s | Export → unresolved excluded | “Download suggested and corrected routes. No account or help-desk system is changed.” |
| 56–60s | Value/end card | “Measured routing. Visible exceptions. A clear human handoff.” |

Gig cut: 60 seconds, muted-safe captions, 1920×1080 H.264 MP4 below 50MB. Keep a readable limitation caption during benchmark: “122 / 2,566 accepted suggestions remain wrong · banking benchmark only.” Static sample shows 32 initial suggestions / 8 review cases and 33 / 7 after correction; these are curated display counts, not benchmark metrics.

Portfolio cut (85 seconds): same arc through 60s, then 60–70s training-only split/threshold evidence, 70–80s official 3,080 vs clean 3,055 and browser/Python parity, 80–85s the synthetic dentist OOD failure and limited production scope. Optional voiceover: “One out-of-domain fixture is wrongly accepted. The margin is not an OOD detector. A real deployment needs buyer-domain evaluation and a separate integration scope.” Thumbnail: hard-case source + two candidates + review badge; never remove the risk disclosure from the benchmark.
