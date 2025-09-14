import streamlit as st
import pandas as pd

# Google Sheets CSV link
sheet_url = "https://docs.google.com/spreadsheets/d/194AEQq3ZZYBiGdBq0OieiAh_AFsVVXJRTGpMQps5fLM/export?format=csv&gid=0"

# Read all columns automatically
df = pd.read_csv(sheet_url)

st.title("Solar Site Data Checker")

# # Show detected columns
# st.write("Detected columns:", df.columns.tolist())

# Select site
site_col = df.columns[0]
site_choice = st.selectbox("Select a site:", df[site_col].unique())

# Filter data for the selected site
site_df = df[df[site_col] == site_choice]

st.subheader("📋 Information for selected site")

# Function to format values (✅/❌)
def format_value(val):
    if pd.isna(val) or str(val).strip() == "":
        return "❌ Not Available"
    else:
        return f"✅ Available ({val})"

# Create formatted copy
formatted_df = site_df.copy()
for col in df.columns[1:]:
    formatted_df[col] = formatted_df[col].apply(format_value)

st.dataframe(formatted_df)

# Quick query
st.subheader("🔎 Quick Query")
field = st.selectbox("Which data do you want to check?", df.columns[1:])
result = site_df[field].iloc[0]

if pd.isna(result) or str(result).strip() == "":
    st.error(f"❌ {field} for {site_choice} is NOT available.")
else:
    st.success(f"✅ {field} for {site_choice} is available ({result})")
