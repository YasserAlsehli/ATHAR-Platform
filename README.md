# ATHAR | أثر

An interactive bilingual decision-support platform for analyzing regional distribution indicators related to Saudi Arabia's nonprofit sector, with a focus on organizations and beneficiaries with disabilities.

## Features

- Arabic and English interface
- Regional distribution analysis across 13 Saudi regions
- Gap-based regional priority classification
- Interactive regional comparisons
- Exploratory K-Means clustering analysis
- Data-driven analytical assistant
- Executive summary and project story
- Region-specific strategic recommendations
- Interactive charts and CSV data export

## Methodology

The distribution gap is measured in percentage points:

**Distribution Gap = Beneficiaries Share (%) − Organizations Share (%)**

Regional priorities are determined by the absolute value of the distribution gap:

- **High Priority:** |Gap| > 3 percentage points
- **Medium Priority:** 1 < |Gap| ≤ 3 percentage points
- **Low Priority:** |Gap| ≤ 1 percentage point

Both positive and negative gaps are considered when determining priority.

The sign of the gap helps guide the interpretation and recommended areas for further investigation.

## Final Results

The approved analysis covers **13 Saudi regions**:

- **3 High Priority regions**
- **5 Medium Priority regions**
- **5 Low Priority regions**

High-priority regions:

| Region | Distribution Gap |
|---|---:|
| Eastern Province | +6.78 pp |
| Qassim | -4.08 pp |
| Riyadh | -3.73 pp |

These classifications indicate relative distribution differences. They do not independently establish service shortages, surpluses, or unmet needs.

## Recommendations

Recommendations consider both the magnitude and direction of each regional gap.

- Positive gaps: investigate service coverage, capacity, accessibility, and potential partnerships.
- Negative gaps: investigate organization specialization, utilization, coordination, and regional coverage.
- Low-priority gaps: continue monitoring and examine differences within regions.

Decisions about service expansion or resource reallocation require additional evidence about actual service needs and coverage.

## Exploratory AI Analysis

K-Means clustering is included as a separate exploratory analysis.

Cluster membership is not equivalent to regional priority and should not be interpreted as a direct measure of service need.

## Technology

- Python
- Pandas
- NumPy
- Plotly
- Scikit-learn
- Streamlit

## Author

Yasser Alsehli

## Important

ATHAR is intended for analytical decision support. All findings should be interpreted alongside data limitations, source context, and additional field evidence.
