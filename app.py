import streamlit as st
import pandas as pd
st.set_page_config(page_title="Bill Splitter", page_icon="💳", layout="centered")

st.markdown("""
<style>
/* Global typography & layout */
h1, h2, h3 {
    text-align: left !important;
    font-family: 'Poppins', sans-serif;
    color: #2c3e50;
}
label, .stTextInput>div>div>input, .stNumberInput>div>div>input {
    font-family: 'Poppins', sans-serif;
}

/* Buttons */
.stButton>button {
    background-color: #2c3e50;
    color: white;
    border-radius: 8px;
    font-weight: bold;
}
.stButton>button:hover {
    background-color: #34495e;
}

/* Card styling */
.card {
    background-color: white;
    padding: 16px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    margin-bottom: 12px;
}

/* Hide all + / - buttons for number inputs (Streamlit 1.38+ compatible) */
div[data-baseweb="input"] input[type=number]::-webkit-inner-spin-button,
div[data-baseweb="input"] input[type=number]::-webkit-outer-spin-button {
    -webkit-appearance: none !important;
    margin: 0 !important;
}

div[data-baseweb="input"] input[type=number] {
    -moz-appearance: textfield !important;
    appearance: textfield !important;
}

/* Hide Streamlit's increment/decrement stepper buttons */
[data-testid="stNumberInput"] button {
    display: none !important;
}

</style>
""", unsafe_allow_html=True)

st.title("Bill Splitter")

with st.expander("🧾 Step 1: Bill Details", expanded=True):
    total_bill = st.number_input("Total bill amount (before tax & service)", min_value=0.0, step=None, format="%.2f")
    total_bill = st.number_input("Total bill amount (before tax & service)", min_value=0.0, step=None, format="%.2f")


    tax_mode = st.radio("Tax input mode", ("Percentage (%)", "Fixed amount"), index=0, horizontal=True)
    if tax_mode == "Percentage (%)":
        tax_percent = st.number_input("Tax (%)", min_value=0.0, step=None, value=10.0, format="%.2f")
        tax_value = None
    else:
        tax_value = st.number_input("Tax amount (fixed)", min_value=0.0, step=None, value=0.0, format="%.2f")
        tax_percent = None

    service_mode = st.radio("Service input mode", ("Percentage (%)", "Fixed amount"), index=0, horizontal=True)
    if service_mode == "Percentage (%)":
        service_percent = st.number_input("Service (%)", min_value=0.0, step=None, value=12.0, format="%.2f")
        service_value = None
    else:
        service_value = st.number_input("Service amount (fixed)", min_value=0.0, step=None, value=0.0, format="%.2f")
        service_percent = None

st.markdown("---")
st.subheader("👥 Step 2: Add Participants and Their Items")

if "participants" not in st.session_state:
    st.session_state.participants = []

with st.form("add_participant", clear_on_submit=True):
    col1, col2 = st.columns([3,1])
    with col1:
        new_name = st.text_input("Participant name", placeholder="e.g. Alice")
    with col2:
        add_btn = st.form_submit_button("Add")
    if add_btn:
        if new_name.strip():
            st.session_state.participants.append({"name": new_name.strip(), "items": []})
        else:
            st.warning("Please enter a valid name.")

if not st.session_state.participants:
    st.info("No participants yet. Add people using the form above.")
else:
    for idx, p in enumerate(st.session_state.participants):
        st.markdown(f"<div class='card'><h3>{p['name']}</h3>", unsafe_allow_html=True)

        if p["items"]:
            df = pd.DataFrame(p["items"], columns=["Item", "Price"])
            st.table(df)

        # Add item form for each participant
        with st.form(f"add_item_{idx}", clear_on_submit=True):
            c1, c2, c3 = st.columns([3,2,1])
            with c1:
                item_name = st.text_input("Item name", key=f"item_name_{idx}", placeholder="e.g. Pizza")
            with c2:
                item_price = st.number_input("Price", min_value=0.0, step=None, key=f"item_price_{idx}", format="%.2f")
            with c3:
                add_item_btn = st.form_submit_button("Add")
            if add_item_btn:
                if item_name.strip():
                    p["items"].append([item_name.strip(), float(item_price)])
                    st.rerun()
                else:
                    st.warning("Please enter an item name.")

        c1, c2 = st.columns([1, 4])
        with c1:
            if st.button("Remove", key=f"remove_{idx}"):
                st.session_state.participants.pop(idx)
                st.rerun()
        with c2:
            if st.button("Clear items", key=f"clear_{idx}"):
                p["items"] = []
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
if st.button("Calculate Split"):
    if total_bill <= 0:
        st.error("Please enter a valid total bill amount greater than 0.")
    elif not st.session_state.participants:
        st.error("No participants added. Please add at least one participant.")
    else:
        subtotals = {p["name"]: sum(it[1] for it in p["items"]) for p in st.session_state.participants}
        total_items_value = sum(subtotals.values())

        computed_tax = tax_value if tax_value is not None else total_bill * (tax_percent / 100.0 if tax_percent is not None else 0)
        computed_service = service_value if service_value is not None else total_bill * (service_percent / 100.0 if service_percent is not None else 0)
        grand_total = total_bill + computed_tax + computed_service

        if total_items_value == 0:
            st.warning("No item prices entered. Splitting total equally.")
            n = len(st.session_state.participants)
            results = [
                {
                    "Person": p["name"],
                    "Subtotal": round(total_bill / n, 2),
                    "Tax Share": round(computed_tax / n, 2),
                    "Service Share": round(computed_service / n, 2),
                    "Total Due": round(grand_total / n, 2),
                }
                for p in st.session_state.participants
            ]
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
        st.success("Split calculated successfully! ✅")
        st.dataframe(df, use_container_width=True)
        st.markdown(f"**Grand Total (bill + tax + service): ${grand_total:.2f}**")

        st.download_button(
            label="Download Breakdown as CSV ⬇️",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="bill_splitter_breakdown.csv",
            mime="text/csv"
        )
