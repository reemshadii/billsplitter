
import streamlit as st
import pandas as pd
from io import BytesIO

# -----------------------
# Page config
# -----------------------
st.set_page_config(page_title="Bill Splitter", page_icon="💳", layout="centered")

# -----------------------
# Theme toggle (light/dark)
# -----------------------

# -----------------------
# CSS for both themes
# -----------------------
light_css = """
<style>
body { background: linear-gradient(120deg,#0b1220,#071225); color: #e6eef8; }
h1, h2, h3 { font-family: 'Poppins', sans-serif; color: #e6eef8; }
.stButton>button { background-color: #06b6d4; color: #042d35; border-radius: 8px; padding: 8px 12px; font-weight:700; }
.card { background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01)); border-radius: 12px; padding: 16px; box-shadow: 0 6px 18px rgba(2,6,23,0.6); }
.small-muted { color: #9ca3af; font-size: 0.9rem; }
</style>
"""

dark_css = """
<style>
body { background: linear-gradient(120deg,#0b1220,#071225); color: #e6eef8; }
h1, h2, h3 { font-family: 'Poppins', sans-serif; color: #e6eef8; }
.stButton>button { background-color: #06b6d4; color: #042d35; border-radius: 8px; padding: 8px 12px; font-weight:700; }
.card { background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01)); border-radius: 12px; padding: 16px; box-shadow: 0 6px 18px rgba(2,6,23,0.6); }
.small-muted { color: #9ca3af; font-size: 0.9rem; }
</style>
"""

st.markdown(light_css if st.session_state.theme == "Light" else dark_css, unsafe_allow_html=True)

# -----------------------
# Header
# -----------------------
st.title("💳 Bill Splitter")
st.write("A fair and precise bill splitting tool — includes tax & service distribution proportional to each person's items.")

# -----------------------
# Input: Bill details
# -----------------------
with st.expander("1) Bill details", expanded=True):
    total_bill = st.number_input("Total bill amount (before tax & service)", min_value=0.0, step=0.01, format="%.2f")
    tax_mode = st.radio("Tax input mode", ("Percentage (%)", "Fixed amount"), index=0, horizontal=True)
    if tax_mode == "Percentage (%)":
        tax_percent = st.number_input("Tax (%)", min_value=0.0, value=10.0, step=0.1)
        tax_value = None
    else:
        tax_value = st.number_input("Tax amount (fixed)", min_value=0.0, value=0.0, step=0.01)
        tax_percent = None

    service_mode = st.radio("Service input mode", ("Percentage (%)", "Fixed amount"), index=0, horizontal=True)
    if service_mode == "Percentage (%)":
        service_percent = st.number_input("Service (%)", min_value=0.0, value=12.0, step=0.1)
        service_value = None
    else:
        service_value = st.number_input("Service amount (fixed)", min_value=0.0, value=0.0, step=0.01)
        service_percent = None

# -----------------------
# Participants input
# -----------------------
st.markdown("---")
st.subheader("2) Participants and their items")
st.write("Add each participant and list the items they ordered. Prices should be per-item (no currency symbol).")

if "participants" not in st.session_state:
    st.session_state.participants = []

# Add participant form
with st.form("add_participant", clear_on_submit=True):
    col1, col2 = st.columns([3,1])
    with col1:
        new_name = st.text_input("Participant name", placeholder="e.g. Alice")
    with col2:
        add_btn = st.form_submit_button("Add")
    if add_btn:
        if new_name and new_name.strip() != "":
            st.session_state.participants.append({"name": new_name.strip(), "items": []})
        else:
            st.warning("Please enter a valid name.")

# Show participants and allow adding items
if not st.session_state.participants:
    st.info("No participants yet. Add people using the form above.")
else:
    for idx, p in enumerate(st.session_state.participants):
        st.markdown(f"<div class='card'><h3>{idx+1}. {p['name']}</h3>", unsafe_allow_html=True)
        # Items table for this participant
        if "items_edit_index" not in st.session_state:
            st.session_state.items_edit_index = {}
        if idx not in st.session_state.items_edit_index:
            st.session_state.items_edit_index[idx] = 0

        # Display existing items in a small table
        if p["items"]:
            df = pd.DataFrame(p["items"], columns=["Item", "Price"])
            st.write("Current items:")
            st.table(df)

        # Add item form
        with st.form(f"add_item_{idx}", clear_on_submit=True):
            c1, c2, c3 = st.columns([3,2,1])
            with c1:
                item_name = st.text_input("Item name", key=f"item_name_{idx}", placeholder="e.g. Pasta")
            with c2:
                item_price = st.number_input("Price", min_value=0.0, step=0.01, key=f"item_price_{idx}")
            with c3:
                add_item_btn = st.form_submit_button("Add")
            if add_item_btn:
                if item_name and item_name.strip() != "":
                    p["items"].append([item_name.strip(), float(item_price)])
                    st.experimental_rerun()
                else:
                    st.warning("Please enter an item name.")

        # Remove participant button
        remove_col1, remove_col2 = st.columns([1,4])
        with remove_col1:
            if st.button("Remove", key=f"remove_{idx}"):
                st.session_state.participants.pop(idx)
                st.experimental_rerun()
        with remove_col2:
            if st.button("Clear items", key=f"clear_{idx}"):
                p["items"] = []
                st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# Calculation
# -----------------------
st.markdown("---")
if st.button("Calculate split"):
    if total_bill <= 0:
        st.error("Please enter a valid total bill amount greater than 0.")
    elif not st.session_state.participants:
        st.error("No participants added. Please add at least one participant.")
    else:
        # Compute subtotals per person
        subtotals = {}
        for p in st.session_state.participants:
            subtotal = sum([it[1] for it in p["items"]]) if p["items"] else 0.0
            subtotals[p["name"]] = subtotal

        total_items_value = sum(subtotals.values())

        # If user provided fixed tax/service, use them; otherwise compute from percent of bill
        computed_tax = tax_value if (tax_value is not None) else (total_bill * (tax_percent / 100.0) if tax_percent is not None else 0.0)
        computed_service = service_value if (service_value is not None) else (total_bill * (service_percent / 100.0) if service_percent is not None else 0.0)

        grand_total = total_bill + computed_tax + computed_service

        if total_items_value == 0:
            # If no item prices entered, fall back to equal split (user warned)
            st.warning("No item prices were entered for any participant. Falling back to equal split of the total bill (including tax & service).")
            n = len(st.session_state.participants)
            equal_share = round(grand_total / n, 2)
            results = []
            for p in st.session_state.participants:
                results.append({
                    "Person": p["name"],
                    "Subtotal": round(grand_total / n, 2),
                    "Tax Share": round(computed_tax / n, 2),
                    "Service Share": round(computed_service / n, 2),
                    "Total Due": equal_share
                })
        else:
            results = []
            for name, subtotal in subtotals.items():
                share_ratio = subtotal / total_items_value
                tax_share = share_ratio * computed_tax
                service_share = share_ratio * computed_service
                total_due = subtotal + tax_share + service_share
                results.append({
                    "Person": name,
                    "Subtotal": round(subtotal, 2),
                    "Tax Share": round(tax_share, 2),
                    "Service Share": round(service_share, 2),
                    "Total Due": round(total_due, 2)
                })

        df = pd.DataFrame(results)
        st.success("Split calculated!")
        st.dataframe(df, use_container_width=True)
        st.markdown(f"**Grand Total (bill + tax + service): {grand_total:.2f}**")

        # Download CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download breakdown (CSV)", data=csv, file_name="bill_splitter_breakdown.csv", mime="text/csv")

        # Copy to clipboard friendly text (streamlit doesn't allow direct clipboard write)
        txt_lines = []
        for r in results:
            txt_lines.append(f"{r['Person']}: {r['Total Due']:.2f} (Subtotal {r['Subtotal']:.2f} + Tax {r['Tax Share']:.2f} + Service {r['Service Share']:.2f})")
        text_blob = "\\n".join(txt_lines)
        st.text_area("Copy-friendly breakdown", value=text_blob, height=200)

# -----------------------
# Footer / Help
# -----------------------
st.markdown("---")
st.markdown("<div class='small-muted'>Tip: add participants first, then add items for each person. Use fixed amounts or percentages for tax/service. This app works offline — press 'Toggle Light / Dark Theme' in the sidebar to switch themes.</div>", unsafe_allow_html=True)
