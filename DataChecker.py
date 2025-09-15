import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Load creds from Streamlit Secrets
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
client = gspread.authorize(creds)
# --- Google Sheets CSV link ---
sheet_url = "https://docs.google.com/spreadsheets/d/194AEQq3ZZYBiGdBq0OieiAh_AFsVVXJRTGpMQps5fLM/export?format=csv&gid=0"
spreadsheet = client.open("Final Solar Data Checker")
worksheet = spreadsheet.worksheet("Sheet1")

# Get all records
data = worksheet.get_all_records()
df = pd.DataFrame(data)
# Read all columns
df = pd.read_csv(sheet_url)

st.title("Solar Site Data Checker")

st.subheader("📋 Status of All Sites")

# --- Format values for table ---
def format_value(val):
    if pd.isna(val) or str(val).strip() == "":
        return "❌ Not Available"

    val = str(val).strip()

    if val.startswith("http") and "drive.google.com" in val:
        file_id = val.split("/d/")[1].split("/")[0]
        preview_url = f"https://drive.google.com/file/d/{file_id}/preview"

        if val.endswith(".pdf") or "pdf" in val.lower():
            return f'<iframe src="{preview_url}" width="300" height="200"></iframe>'
        else:
            return f'<a href="{val}" target="_blank">🔗 Document</a>'

    elif val.startswith("http"):
        return f'<a href="{val}" target="_blank">🔗 Document</a>'

    else:
        return f"✅ Available ({val})"

# Format DataFrame
formatted_df = df.copy()
for col in formatted_df.columns[1:]:
    formatted_df[col] = formatted_df[col].apply(format_value)

html_table = formatted_df.to_html(escape=False, index=False)

scrollable_table = f"""
<div style="display: flex; justify-content: center; margin-top: 10px;">
  <div style="width: 100%; max-width: 800px; height: 400px; overflow: auto; border: 1px solid #ddd; padding: 5px;">
    <style>
      table {{
        border-collapse: collapse;
        font-size: 12px;
        white-space: nowrap;
      }}
      th {{
        text-align: center !important;
        vertical-align: middle !important;
        background-color: #ffffff;
        color: #000000;
        padding: 8px 12px;
      }}
      td {{
        text-align: center;
        vertical-align: middle;
        padding: 6px 10px;
      }}
    </style>
    {html_table}
  </div>
</div>
"""
st.markdown(scrollable_table, unsafe_allow_html=True)



# --- Quick Query ---
st.subheader("🔎 Quick Query")
site_col = df.columns[0]
site_choice = st.selectbox("Choose a site for quick check:", df[site_col].unique())
field = st.selectbox("Which data do you want to check?", df.columns[1:])
result = df[df[site_col] == site_choice][field].iloc[0]

if pd.isna(result) or str(result).strip() == "":
    st.error(f"❌ {field} for {site_choice} is NOT available.")
else:
    st.success(f"✅ {field} for {site_choice} is available ({result})")
