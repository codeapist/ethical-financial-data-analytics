from __future__ import annotations

from datetime import datetime, timezone
import hashlib

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Ethical Finance Analytics", page_icon="📊", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
.small-note {font-size: .88rem; opacity: .8;}
</style>
""", unsafe_allow_html=True)

st.title("Ethical Financial Data Analytics")
st.caption("A responsible-AI prototype for consent-based transaction insights")

if "audit_events" not in st.session_state:
    st.session_state.audit_events = []
if "consent" not in st.session_state:
    st.session_state.consent = False


def audit(event: str, detail: str) -> None:
    st.session_state.audit_events.append({
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "event": event,
        "detail": detail,
    })


def make_demo_data(n_customers: int = 240, seed: int = 41) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    categories = ["Housing", "Groceries", "Transport", "Dining", "Shopping", "Utilities", "Health", "Entertainment"]
    category_weights = np.array([.24, .18, .10, .10, .11, .09, .08, .10])
    for i in range(1, n_customers + 1):
        income = float(np.clip(rng.normal(52000, 19000), 16000, 140000))
        age = int(rng.integers(18, 70))
        age_group = "18–29" if age < 30 else ("30–49" if age < 50 else "50+")
        income_band = "Lower" if income < 35000 else ("Middle" if income < 70000 else "Higher")
        customer_id = f"C{i:04d}"
        monthly_spend = income * float(rng.uniform(.48, .88))
        month_weights = rng.dirichlet(category_weights * 35)
        for month in range(1, 7):
            month_spend = monthly_spend * float(rng.normal(1, .09))
            amounts = rng.multinomial(max(1, int(month_spend)), month_weights)
            for category, amount in zip(categories, amounts):
                if amount <= 0:
                    continue
                rows.append({
                    "customer_id": customer_id,
                    "age_group": age_group,
                    "income_band": income_band,
                    "monthly_income_inr": round(income, 2),
                    "month": f"2026-{month:02d}",
                    "category": category,
                    "amount_inr": float(amount),
                })
    return pd.DataFrame(rows)


def mask_customer_ids(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["customer_id"] = out["customer_id"].astype(str).map(
        lambda value: "ID-" + hashlib.sha256(value.encode()).hexdigest()[:8]
    )
    return out


def summarize_spending(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("category", as_index=False)["amount_inr"].sum().sort_values(
        "amount_inr", ascending=False
    )


def fairness_summary(df: pd.DataFrame) -> pd.DataFrame:
    # Illustrative parity check. Group attributes are used for auditing only,
    # never as inputs to the prompt rule.
    customer = df.groupby(
        ["customer_id", "age_group", "income_band", "category"], as_index=False
    )["amount_inr"].sum()
    wide = customer.pivot_table(
        index=["customer_id", "age_group", "income_band"],
        columns="category", values="amount_inr", fill_value=0
    ).reset_index()
    if wide.empty:
        return pd.DataFrame(columns=["group_type", "group", "customers", "prompt_rate_pct"])
    discretionary_categories = [
        c for c in ["Dining", "Shopping", "Entertainment"] if c in wide.columns
    ]
    wide["discretionary_spend"] = wide[discretionary_categories].sum(axis=1)
    threshold = float(wide["discretionary_spend"].median())
    wide["received_prompt"] = wide["discretionary_spend"] > threshold
    rows = []
    for field in ["age_group", "income_band"]:
        for group, part in wide.groupby(field):
            rows.append({
                "group_type": field,
                "group": group,
                "customers": len(part),
                "prompt_rate_pct": round(100 * part["received_prompt"].mean(), 1),
            })
    return pd.DataFrame(rows)


demo = make_demo_data()

with st.sidebar:
    st.header("Responsible-use controls")
    st.write("**Data source:** deterministic synthetic transactions")
    consent = st.checkbox(
        "I consent to run personalized insights on the demo data.",
        value=st.session_state.consent,
        help="This checkbox simulates a consent gate. It is not a legal consent-management system.",
    )
    if consent != st.session_state.consent:
        st.session_state.consent = consent
        audit("consent_updated", "Consent granted" if consent else "Consent withdrawn")
    st.divider()
    st.subheader("Data minimization")
    use_aggregates = st.toggle("Show category aggregates", value=True)
    mask_ids = st.toggle("Mask customer identifiers", value=True)
    st.caption("Demographic attributes are reserved for fairness auditing and are not used to generate insights.")
    st.divider()
    st.subheader("Prototype status")
    st.success("Synthetic data only")
    st.warning("Not production banking software")

view_df = mask_customer_ids(demo) if mask_ids else demo.copy()

if not st.session_state.consent:
    st.info("Personalized analysis is disabled until consent is enabled in the sidebar.")
    st.markdown("### Why consent matters")
    st.write(
        "The prototype demonstrates an opt-in gate: no customer-level insight panel is shown before consent. "
        "A production system should also support consent records, withdrawal, purpose limitation, and deletion workflows."
    )
else:
    audit("analysis_run", "Personalized insights generated from synthetic data")
    st.success("Consent is enabled for this demo session. Insights below use synthetic data.")
    total_spend = float(demo["amount_inr"].sum())
    customer_count = int(demo["customer_id"].nunique())
    mean_income = float(demo.drop_duplicates("customer_id")["monthly_income_inr"].mean())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Demo customers", f"{customer_count:,}")
    c2.metric("Transaction records", f"{len(demo):,}")
    c3.metric("Six-month spend", f"₹{total_spend:,.0f}")
    c4.metric("Avg. monthly income", f"₹{mean_income:,.0f}")

    left, right = st.columns(2)
    with left:
        st.subheader("Spending by category")
        category_summary = summarize_spending(demo)
        fig = px.bar(
            category_summary, x="category", y="amount_inr",
            title="Aggregate transaction spend",
            labels={"category": "Category", "amount_inr": "Spend (INR)"},
        )
        fig.update_layout(xaxis_tickangle=-25, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Monthly spending trend")
        monthly = demo.groupby("month", as_index=False)["amount_inr"].sum()
        fig = px.line(
            monthly, x="month", y="amount_inr", markers=True,
            labels={"month": "Month", "amount_inr": "Spend (INR)"},
        )
        fig.update_layout(margin=dict(l=10, r=10, t=25, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Illustrative personalized insight")
    discretionary = demo[
        demo["category"].isin(["Dining", "Shopping", "Entertainment"])
    ].groupby("customer_id")["amount_inr"].sum()
    median_discretionary = float(discretionary.median())
    selected_id = st.selectbox("Choose a synthetic customer", sorted(demo["customer_id"].unique()))
    customer_data = demo[demo["customer_id"] == selected_id]
    customer_discretionary = float(
        customer_data[customer_data["category"].isin(["Dining", "Shopping", "Entertainment"])]["amount_inr"].sum()
    )
    if customer_discretionary > median_discretionary:
        st.write(
            "**Suggested prompt:** Review dining, shopping, and entertainment spending "
            "to see whether a monthly savings target is realistic."
        )
    else:
        st.write(
            "**Suggested prompt:** Consider setting a small automatic savings goal "
            "and reviewing recurring bills."
        )
    st.caption(
        "These prompts are simple demonstrations, not financial advice. The same rule is applied to all customers "
        "and does not use age or income group."
    )

    st.subheader("Fairness monitoring")
    fair = fairness_summary(demo)
    st.write(
        "Prompt rates are compared across synthetic demographic groups as a screening check. "
        "A difference is a signal to investigate, not proof of discrimination or fairness."
    )
    st.dataframe(fair, hide_index=True, use_container_width=True)
    if not fair.empty:
        fig = px.bar(
            fair, x="group", y="prompt_rate_pct", color="group_type", barmode="group",
            labels={
                "group": "Group",
                "prompt_rate_pct": "Customers receiving prompt (%)",
                "group_type": "Audit dimension",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Minimized transaction preview"):
        if use_aggregates:
            preview = (
                demo.groupby(["month", "category"], as_index=False)["amount_inr"]
                .sum()
                .sort_values(["month", "category"])
                .head(30)
            )
            st.caption("Showing monthly category totals; customer identifiers are omitted from this aggregate.")
        else:
            preview_cols = ["customer_id", "month", "category", "amount_inr"]
            preview = view_df[preview_cols].head(30)
            st.caption("Showing a limited synthetic transaction preview. Identifiers are masked by default.")
        st.dataframe(preview, hide_index=True, use_container_width=True)
        st.caption(
            "The demo data is generated in memory and is not uploaded to a server by this application."
        )

st.divider()
st.header("Governance checklist")
checklist = pd.DataFrame([
    {"Control": "Consent and purpose limitation", "Implementation": "Opt-in gate before insights", "Status": "Demonstrated"},
    {"Control": "Data minimization", "Implementation": "Aggregate charts and restricted preview columns", "Status": "Demonstrated"},
    {"Control": "Privacy", "Implementation": "Synthetic data; optional hashed identifiers", "Status": "Demonstrated"},
    {"Control": "Bias and fairness", "Implementation": "Group-level prompt-rate comparison", "Status": "Illustrative only"},
    {"Control": "Security", "Implementation": "No secrets or real customer data; production controls documented", "Status": "Partial"},
    {"Control": "Accountability", "Implementation": "Session audit log and CSV export", "Status": "Demonstrated"},
])
st.dataframe(checklist, hide_index=True, use_container_width=True)

st.subheader("Audit log")
audit_df = pd.DataFrame(
    st.session_state.audit_events, columns=["timestamp_utc", "event", "detail"]
)
if audit_df.empty:
    st.caption("No actions recorded in this session yet.")
else:
    st.dataframe(audit_df, hide_index=True, use_container_width=True)
    st.download_button(
        "Download audit log (CSV)",
        audit_df.to_csv(index=False).encode("utf-8"),
        file_name="ethical_finance_audit_log.csv",
        mime="text/csv",
    )

st.caption(
    "Academic prototype only. Do not upload real financial records. Production deployment requires legal review, "
    "threat modelling, secure identity management, retention/deletion controls, and independent model validation."
)
