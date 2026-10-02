# Real data and rights

Source: **BANKING77**, released by PolyAI, Iñigo Casanueva, Tadas Temčinas, Daniela Gerz, Matthew Henderson and Ivan Vulić, *Efficient Intent Detection with Dual Sentence Encoders* (2020). [Publisher repository](https://github.com/PolyAI-LDN/task-specific-datasets), [primary paper](https://aclanthology.org/2020.nlp4convai-1.5/), [publisher licence](https://github.com/PolyAI-LDN/task-specific-datasets/blob/master/LICENSE).

The publisher explicitly licenses shared datasets under **Creative Commons Attribution 4.0 International**. Commercial demonstration is permitted with attribution, licence and change notices; no endorsement is implied. Full terms are in [data/LICENSE-CC-BY-4.0.txt](data/LICENSE-CC-BY-4.0.txt). Software is MIT; the redistributed dataset excerpts and dataset-derived model assets retain CC BY 4.0 attribution. No logos, private account records or seller client data are used.

Immutable publisher commit: `57ec275d8078af65b7731c2a98be812d844a6d6b`. Original publisher bytes acquired **2 October 2026**, independently hash-verified by this build and re-downloaded from the immutable commit by the acquisition script on **3 October 2026**. [Machine-readable source URLs, SHA-256, byte counts and latest retrieval dates](data/provenance.json). `scripts/acquire.py` fetches the public source at that commit and refuses any changed checksum. `--verified-cache` is for previously acquired bytes with matching SHA-256; it does not claim a new network retrieval.

| File | Rows | SHA-256 |
|---|---:|---|
| Train CSV | 10,003 | `b06e26ac675513959a63135f11b94ea7786ed02da65db93a5650d8838cbc664b` |
| Test CSV | 3,080 | `d12d6e3bc4c3103966ae786dc435913c0c563dfa328f5a3646d0e62cfeeb474d` |

Both splits have 77 intents. The paper describes customer-service queries with fine-grained overlapping intents. The inspected primary sources do not document the complete collection chain: this project does **not** claim untouched live-bank logs or production representativeness.

Preprocessing: lowercase text; word tokens of at least two characters; adjacent word bigrams; sublinear term frequency, smoothed IDF and L2 normalization. Vocabulary capped at 8,000 features. Training-validation grouping uses lowercase followed by Python `re.sub(r'\W+', ' ', text).strip()`. One seeded (`42`) stratified-group five-fold split supplies **8,002 development / 2,001 validation** rows; normalized groups do not cross that boundary. Neither vocabulary nor coefficients use validation/test data. Threshold selection uses validation only; no refit on the entire training split and no test-driven tuning.

The official test contains **25 normalized text overlaps** with the complete training split (zero exact-text overlaps). Report both official 3,080-row and deduplicated **3,055-row** results. [Overlap IDs and training split IDs](evaluation/split.json). This removes all overlaps with training, even where a matching row was validation-only. It is not deduplication based on observed test correctness.

The committed [40-message offline sample](public/sample.json) preserves real source text and zero-based official test IDs. It is curated **after measurement** to show eight review cases, including three wrong first suggestions, and 32 correct accepted examples. It is not a representative evaluation sample or denominator. Labels reside only in `evaluation/sample-audit.json`; that file is absent from the deployed site and is not an inference input. No synthetic text is used in real-data accuracy. Four explicitly authored, labelled synthetic OOD fixtures live separately in `evaluation/ood-fixtures.json`; one is wrongly accepted, demonstrating that margin is not an OOD detector.

Model weights are rounded to nine decimals for browser export, with independent Python/browser parity verification. Browser input is text only; no row-ID answer lookup, ground-truth category, test split or OOD label is passed to the classifier. Class identifiers are the output taxonomy; displaying candidate class names is necessary for routing.

The demo maps each predicted intent to an identically named queue for inspection. This is a design choice, not a bank's organizational taxonomy. The data is historical/public; no banking actions, customer accounts, regulated advice or automated replies are demonstrated.
