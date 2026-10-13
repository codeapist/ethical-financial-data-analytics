# Ethical Financial Data Analytics

A Streamlit academic prototype demonstrating responsible AI practices for using customer transaction data to generate personalized financial insights.

## Case-study objectives

- **Consent:** Personalization is gated behind an explicit opt-in control.
- **Data minimization:** The interface prioritizes aggregate charts and a limited transaction preview.
- **Privacy:** Uses deterministic synthetic transactions and supports masking displayed customer identifiers.
- **Bias and fairness:** Compares recommendation-prompt rates across synthetic age and income groups.
- **Security:** Avoids real customer records and secrets; production security gaps are documented.
- **Accountability:** Records session events and supports CSV export of the audit trail.

## Technology stack

Python, Streamlit, Pandas, NumPy, and Plotly.

## Repository contents

- `app.py` — interactive analytics dashboard
- `requirements.txt` — Python dependencies
- `docs/ETHICAL_FRAMEWORK.md` — responsible AI governance framework
- `LICENSE` — MIT license
- `.gitignore` — excludes local environments and secret files

## Publish a live demo without running it locally

1. Open [Streamlit Community Cloud](https://share.streamlit.io/).
2. Sign in and connect your GitHub account if prompted.
3. Choose **Create app**, then select this repository: `codeapist/ethical-financial-data-analytics`.
4. Set the branch to `main` and the main file path to `app.py`.
5. Deploy the app. Streamlit will install the packages listed in `requirements.txt`.

Pushing code to GitHub does not by itself make the app live; deployment is a separate step.

## Data safety and limitations

The dashboard creates synthetic data in memory and does not require real financial records. Do not add or upload real customer financial data, account numbers, credentials, or secrets.

This is an educational proof of concept, not a production banking product, compliance certification, or financial-advice service. The consent checkbox is a demonstration, hashing is pseudonymization rather than anonymization, fairness comparisons are screening indicators rather than proof of fairness, and the session audit log is temporary and not tamper-proof. Production use would require privacy/legal review, threat modelling, robust identity and access management, retention and deletion controls, and independent validation.

## Suggested demonstration

1. Open the dashboard and show that personalized insights are disabled before consent.
2. Enable consent and review the aggregate spending charts.
3. Select a synthetic customer to see an illustrative savings prompt.
4. Review subgroup prompt rates in the fairness monitoring section.
5. Review the governance checklist and download the session audit log.
