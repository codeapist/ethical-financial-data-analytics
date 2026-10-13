# Ethical Financial Data Analytics

A Streamlit prototype demonstrating responsible use of synthetic customer transaction data for personalized financial insights.

## Case-study objectives

- Consent: explicit opt-in before personalized analysis.
- Data minimization: keep the analysis to necessary transaction fields.
- Privacy: demonstrate masking and aggregation.
- Bias and fairness: explore recommendation differences across synthetic groups.
- Security: demonstrate safer data-handling patterns.
- Accountability: log consent changes and analysis actions.

## Stack

- Python
- Streamlit
- Pandas and NumPy
- Plotly

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data and limitations

The app uses synthetic demonstration data only. Do not upload real customer financial records. This is an educational prototype, not a production banking system, compliance certification, or financial-advice service. Its consent and fairness features illustrate concepts but do not establish legal compliance or prove absence of bias.

## Project structure

- `app.py` — interactive dashboard
- `requirements.txt` — Python dependencies
- `docs/ETHICAL_FRAMEWORK.md` — governance framework
- `LICENSE` — MIT license
