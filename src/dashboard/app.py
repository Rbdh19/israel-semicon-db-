import streamlit as st
import httpx
import pandas as pd

API_URL = "https://israel-semicon-db-production.up.railway.app"

st.set_page_config(page_title="Israel Semicon DB", layout="wide", page_icon="🇮🇱")

@st.cache_data(ttl=300)
def fetch_stats():
    r = httpx.get(f"{API_URL}/companies/stats", timeout=10)
    return r.json()

def fetch_companies(search="", sub_sectors=None, company_types=None, city="", page=1):
    params = {"page": page, "page_size": 100}
    if search: params["search"] = search
    if sub_sectors:
        for s in sub_sectors:
            params["sub_sector"] = s
    if company_types:
        for t in company_types:
            params["company_type"] = t
    if city: params["hq_city"] = city
    r = httpx.get(f"{API_URL}/companies", params=params, timeout=15)
    return r.json()

def fetch_company(company_id):
    r = httpx.get(f"{API_URL}/companies/{company_id}", timeout=10)
    return r.json()

with st.sidebar:
    st.title("🇮🇱 Israel Semicon DB")
    st.caption("186 Israeli semiconductor companies")
    st.divider()
    search = st.text_input("🔍 Search company name", placeholder="e.g. Hailo, Tower...")
    sub_sectors = st.multiselect("Sub-sector",
        ["fabless", "photonics", "rf_wireless", "eda", "automotive", "defense", "ip_licensing", "mixed_signal"])
    company_types = st.multiselect("Company type", ["private", "public", "acquired"])
    city = st.text_input("City", placeholder="e.g. Tel Aviv")
    st.divider()
    st.caption("Data: Israeli Companies Registrar + public sources")

st.markdown("## 🏭 Israeli Semiconductor Company Database")

stats = fetch_stats()
data = fetch_companies(search, sub_sectors, company_types, city)
results = data.get("results", [])
total = data.get("total", 0)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Companies shown", total)
c2.metric("Private", stats["by_type"].get("private", 0))
c3.metric("Public", stats["by_type"].get("public", 0))
avg_q = sum(r.get("data_quality_score", 0) for r in results) / len(results) if results else 0
c4.metric("Avg quality", f"{avg_q:.2f}")

st.divider()

if not results:
    st.info("No companies found. Try adjusting filters.")
else:
    df = pd.DataFrame([{
        "company_id": r["company_id"],
        "Company": r.get("name_en", ""),
        "Type": r.get("company_type", ""),
        "Sub-sector": ", ".join(r.get("sub_sector") or []),
        "City": r.get("hq_city", ""),
        "Founded": r.get("founded_year"),
        "Employees": r.get("employee_count_est"),
        "Quality": r.get("data_quality_score", 0),
    } for r in results])

    st.dataframe(
        df.drop(columns=["company_id"]),
        use_container_width=True,
        column_config={
            "Quality": st.column_config.ProgressColumn("Quality", min_value=0, max_value=1, format="%.2f"),
            "Founded": st.column_config.NumberColumn("Founded", format="%d"),
            "Employees": st.column_config.NumberColumn("Employees", format="%d"),
        },
        hide_index=True,
    )

    st.divider()
    st.subheader("Company Detail")
    names = [r.get("name_en", "") for r in results]
    ids = [r["company_id"] for r in results]
    selected = st.selectbox("Select a company", names)
    if selected:
        idx = names.index(selected)
        detail = fetch_company(ids[idx])
        with st.expander(f"📋 {selected}", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**Identifiers**")
                st.write(f"Company #: `{detail.get('company_number', '—')}`")
                st.write(f"Type: {detail.get('company_type', '—')}")
                st.write(f"Status: {detail.get('status', '—')}")
                st.write(f"Founded: {detail.get('founded_year', '—')}")
            with col2:
                st.markdown("**Sector & Size**")
                st.write(f"Sub-sector: {', '.join(detail.get('sub_sector') or ['—'])}")
                st.write(f"City: {detail.get('hq_city', '—')}")
                st.write(f"Employees: {detail.get('employee_count_est', '—')}")
            with col3:
                st.markdown("**Funding**")
                st.write(f"Last round: {detail.get('last_funding_date', '—')}")
                amt = detail.get('last_funding_amount_usd')
                st.write(f"Amount: {'${:,.0f}'.format(amt) if amt else '—'}")
                total_f = detail.get('total_funding_usd')
                st.write(f"Total: {'${:,.0f}'.format(total_f) if total_f else '—'}")
            if detail.get("description"):
                st.markdown(f"**About:** {detail['description']}")
            st.progress(detail.get("data_quality_score", 0),
                       text=f"Data quality: {detail.get('data_quality_score', 0):.0%}")

with st.expander("📊 Coverage Analytics"):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("By Sub-sector")
        sector_df = pd.DataFrame(list(stats["by_sector"].items()), columns=["Sector", "Count"])
