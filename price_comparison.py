import os

import pandas as pd
import streamlit as st


# Define constants
CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "..",
    "data/materials.csv",
)
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
def load_material_data(csv_path, empty_data):
    if os.path.isfile(csv_path):
        return pd.read_csv(csv_path)
    else:
        return pd.DataFrame(empty_data)


def append_to_csv(dataframe, csv_file_path, sep=","):
    if os.path.isfile(csv_file_path):
        if os.path.getsize(csv_file_path) > 0:
            # File exists and is not empty, load its data
            existing_df = pd.read_csv(csv_file_path, sep=sep)
            updated_df = pd.concat([existing_df, dataframe])

            # Avoiding duplicates
            updated_df.drop_duplicates(inplace=True)

            updated_df.to_csv(csv_file_path, index=False, sep=sep)
        else:
            # File exists but is empty, write the dataframe
            dataframe.to_csv(csv_file_path, index=False, sep=sep)
    else:
        # File does not exist, write the dataframe
        dataframe.to_csv(csv_file_path, index=False, sep=sep)


st.set_page_config(page_title="Some Calculations", layout="wide")
st.title("Calculations")
col0, col1, col2, col3, col4 = st.columns(
    [2, 1, 1, 1, 1],
    gap="small",
)

material_df = load_material_data(CSV_PATH, EMPTY_MATERIAL_DATA)
if "data" not in st.session_state:
    st.session_state.material_df = material_df.to_dict()
with col0:
    st.text_input(label="Product Name or Number", key="product_identifier")
    st.text_input(label="URL", key="link")
with col1:
    st.number_input(label="Length", step=10, key="material_length", help="in mm")
    st.number_input(label="Width", step=10, key="material_width", help="in mm")
    st.number_input(label="Height", step=10, key="material_height", help="in mm")
with col2:
    st.number_input(label="Amount", step=1, key="material_amount")
    st.number_input(label="Price", step=1.0, key="material_price", help="in €")
with col3:
    pass

if st.button("Calculate"):
    input_values = [
        st.session_state.get("material_width", None),
        st.session_state.get("material_length", None),
        st.session_state.get("material_height", None),
        st.session_state.get("material_amount", None),
        st.session_state.get("material_price", None),
        st.session_state.get("link", None),
        st.session_state.get("product_identifier", None),
    ]

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

    input_values.append(qm)
    input_values.append(price_per_unit)
    input_values.append(price_per_qm)

    with col3:
        pass
        # st.write(width_in_meters)
        # st.write(length_in_meters)
        # st.write(single_amount_square_meters)
        # st.write(st.session_state.material_amount)
        # st.write(
        #     f"{width_in_meters} * {length_in_meters} = {single_amount_square_meters}\n{single_amount_square_meters} * {st.session_state.material_amount} = {st.session_state.material_amount * single_amount_square_meters}"
        # )

    with col4:
        st.write(f"{qm:.2f} qm")
        st.write(f"{price_per_qm:.2f} € per qm")
        st.write(f"{price_per_unit:.2f} € per unit")

    for key, value in zip(EMPTY_MATERIAL_DATA.keys(), input_values):
        EMPTY_MATERIAL_DATA[key].append(value)
    material_df = pd.DataFrame.from_dict(EMPTY_MATERIAL_DATA, orient="columns")
    append_to_csv(material_df, CSV_PATH)

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

material_data = load_material_data(CSV_PATH, EMPTY_MATERIAL_DATA)

csv_string = material_data.to_csv(index=False)

st.download_button(
    "Download Data as CSV",
    data=csv_string,
    file_name="Plywood Price Comparison.csv",
)


st.bar_chart(material_data, x="product_identifier", y="price_per_qm")
st.dataframe(
    material_data,
    column_order=output_order,
)
