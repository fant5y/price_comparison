import os

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Some Calculations", layout="wide")


# Define constants
CSV_PATH = "materials.csv"

EMPTY_MATERIAL_DATA = {
    "width": [],
    "length": [],
    "height": [],
    "amount": [],
    "price": [],
    "link": [],
    "product_identifier": [],
    "qm": [],
    "price_per_unit": [],
    "price_per_qm": [],
}



# Function to load data from csv file or return an empty dataframe
def load_material_data():
    if os.path.isfile(CSV_PATH):
        if os.path.getsize(CSV_PATH) <= 0:
            return pd.DataFrame(EMPTY_MATERIAL_DATA)
        else:
            return pd.read_csv(CSV_PATH)

    else:
        return pd.DataFrame(EMPTY_MATERIAL_DATA)


def append_to_csv(dataframe, sep=","):
    if os.path.isfile(CSV_PATH):
        if os.path.getsize(CSV_PATH) > 0:
            # File exists and is not empty, load its data
            existing_df = pd.read_csv(CSV_PATH, sep=sep)
            updated_df = pd.concat([existing_df, dataframe])

            # Avoiding duplicates
            updated_df.drop_duplicates(inplace=True)

            updated_df.to_csv(CSV_PATH, index=False, sep=sep)
            st.info(f"Updated Data in CSV: {CSV_PATH}", icon="💾")
        else:
            # File exists but is empty, write the dataframe
            dataframe.to_csv(CSV_PATH, index=False, sep=sep)
            st.info(f"Saved Data to the new CSV: {CSV_PATH}", icon="💾")
    else:
        # File does not exist, write the dataframe
        dataframe.to_csv(CSV_PATH, index=False, sep=sep)


def update_csv(dataframe, sep=","):
    # This function is to be used when existing data is updated
    dataframe.to_csv(CSV_PATH, index=False, sep=sep)
    st.info(f"Updated data in CSV: {CSV_PATH}", icon="💾")


def calculate_prices(material_list):
    width_in_meters = st.session_state.get("material_width") / 1000
    length_in_meters = st.session_state.get("material_length") / 1000
    single_amount_square_meters = width_in_meters * length_in_meters

    qm = (
        (single_amount_square_meters * st.session_state.material_amount)
        if st.session_state.material_width != 0
        else 0
    )
    price_per_unit = (
        st.session_state.material_price / st.session_state.material_amount
        if st.session_state.material_amount != 0
        else 0
    )
    price_per_qm = st.session_state.material_price / qm if qm != 0 and not None else 0

    material_list.append(qm)
    material_list.append(price_per_unit)
    material_list.append(price_per_qm)

    with st.sidebar:
        st.write(f"{qm:.2f} qm")
        st.write(f"{price_per_qm:.2f} € per qm")
        st.write(f"{price_per_unit:.2f} € per unit")

    return material_list



st.title("Calculations")
col0, col1, col2, col3, col4 = st.columns(
    [2, 1, 1, 1, 1],
    gap="small",
)

material_df = load_material_data()

if "data" not in st.session_state:
    st.session_state.material_df = material_df.to_dict()

with st.sidebar:
    st.text_input(label="Product Name or Number", key="product_identifier")
    st.text_input(label="URL", key="link")
    st.number_input(label="Length", step=10, key="material_length", help="in mm")
    st.number_input(label="Width", step=10, key="material_width", help="in mm")
    st.number_input(label="Height", step=10, key="material_height", help="in mm")
    st.number_input(label="Amount", step=1, key="material_amount")
    st.number_input(label="Price", step=1.0, key="material_price", help="in €")

    if st.button("Calculate and Save", use_container_width=True):
        input_values = [
            st.session_state.get("material_width", None),
            st.session_state.get("material_length", None),
            st.session_state.get("material_height", None),
            st.session_state.get("material_amount", None),
            st.session_state.get("material_price", None),
            st.session_state.get("link", None),
            st.session_state.get("product_identifier", None),
        ]

        input_values = calculate_prices(input_values)

        for key, value in zip(EMPTY_MATERIAL_DATA.keys(), input_values):
            EMPTY_MATERIAL_DATA[key].append(value)

        material_df = pd.DataFrame.from_dict(EMPTY_MATERIAL_DATA, orient="columns")
        append_to_csv(material_df)
        st.session_state.clear()

output_order = [
    "product_identifier",
    "price_per_qm",
    "qm",
    "price_per_unit",
    "width",
    "length",
    "height",
    "amount",
    "price",
    "link",
]

material_data = load_material_data()

csv_string = material_data.to_csv(index=False)

st.download_button(
    "Download Data as CSV",
    data=csv_string,
    file_name="Plywood Price Comparison.csv",
)

st.bar_chart(material_data, x="product_identifier", y="price_per_qm")

edited_material_data = st.data_editor(
    material_data,
    column_order=output_order,
    column_config={
        "price": st.column_config.NumberColumn("Price", format="%.2f €"),
        "price_per_qm": st.column_config.NumberColumn("Price/m²", format="%.2f €"),
        "price_per_unit": st.column_config.NumberColumn("Price/Unit", format="%.2f €"),
        "width": st.column_config.NumberColumn("Width in mm", format="%d mm"),
        "length": st.column_config.NumberColumn("Length in mm", format="%d mm"),
        "height": st.column_config.NumberColumn("Height in mm", format="%d mm"),
        "qm": st.column_config.NumberColumn("Square Meter", format="%.4f m²"),
        "link": st.column_config.LinkColumn("Product URL", ),
        "product_identifier": st.column_config.TextColumn("Product")
    }, hide_index=True, num_rows="dynamic"
)

if st.button('Save Changes', key='save-changes'):
    st.write(edited_material_data)
    update_csv(edited_material_data)
