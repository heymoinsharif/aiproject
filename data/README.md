# Dataset Documentation: Phishing Email Corpus

## 1. Overview & Provenance
This project utilizes the **CEAS 2008 (Collaboration to Evaluate Advanced Spamanalyses)** benchmark phishing email dataset, widely recognized in academic peer-reviewed literature for training and benchmarking email security classifiers.

- **Primary Source**: CEAS 2008 Conference & Spam Challenge (Collaboration to Evaluate Advanced Spamanalyses)
- **Archive Mirrors**: Open cybersecurity benchmark repository (`PHP4Life/Phishing-Email-Dataset` and CEAS public archive)
- **License**: Public Domain / Research and Academic Use
- **Citation**:
  ```bibtex
  @misc{ceas2008challenge,
    title={CEAS 2008 Spam and Phishing Email Challenge Dataset},
    author={Collaboration to Evaluate Advanced Spamanalyses},
    year={2008},
    howpublished={\url{http://www.ceas.cc/2008/}}
  }
  ```

## 2. Dataset Schema
The raw dataset (`CEAS_08.csv`) and processed benchmark (`phishing_emails.csv`) include the following attributes:

| Field | Type | Description |
|---|---|---|
| `sender` | String | Email sender header (`From:` address and display name) |
| `receiver` | String | Target recipient address |
| `date` | String | Delivery/transmission timestamp |
| `subject` | String | Subject line header of the email |
| `body` | String | Plain-text / decoded HTML message body content |
| `urls` | Integer | Count of hyperlink references identified in the email |
| `label` | Integer | Ground truth target: `1` = Phishing, `0` = Legitimate / Safe |

## 3. Dataset Integrity & Hygiene
The dataset ingestion pipeline (`src/data_loader.py`) enforces strict validation checks:
1. **Missing Value Imputation**: Missing subject or body lines are safely handled without data loss; records where both subject and body are null are purged.
2. **Deduplication**: Exact duplicate messages and identical spam template repetitions are pruned to eliminate bias and prevent artificial inflation of test accuracy.
3. **Label Normalization**: Canonical binary encoding:
   - `1`: Phishing attack email
   - `0`: Legitimate email (ham)
4. **Data Leakage Prevention**: Stratified train/test splitting is performed *before* any feature extraction, scaling, or vocabulary fitting. All vectorizers are fitted exclusively on the training partition.

## 4. Benchmark Statistics
- **Total Raw Records**: 39,154 emails
- **Raw Phishing Count**: 21,842 (55.8%)
- **Raw Legitimate Count**: 17,312 (44.2%)
- **Curated Benchmark Partition**: 10,000 stratified emails for efficient, reproducible cross-validation and benchmarking.
