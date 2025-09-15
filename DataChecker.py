import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- Load creds from Streamlit Secrets ---
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
client = gspread.authorize(creds)

# --- Open Spreadsheet (اسم شیت اصلیت رو درست بذار) ---
spreadsheet = client.open("Solar_Sites")   # 👈 اسم شیت اصلی
worksheet = spreadsheet.worksheet("Sheet1")  # 👈 اسم تب (worksheet)
data = worksheet.get_all_records()
df = pd.DataFrame(data)

st.title("🌞 Solar Site Data Checker (Secure)")

# --- Format values ---
def format_value(val):
    if pd.isna(val) or str(val).strip() == "":
        return "❌ Not Available"

    val = str(val).strip()

    if val.startswith("http") and "drive.google.com" in val:
        try:
            file_id = val.split("/d/")[1].split("/")[0]
            preview_url = f"https://drive.google.com/file/d/{file_id}/preview"
            if val.endswith(".pdf") or "pdf" in val.lower():
                return f'<iframe src="{preview_url}" width="300" height="200"></iframe>'
            else:
                return f'<a href="{val}" target="_blank">🔗 Document</a>'
        except Exception:
            return f'<a href="{val}" target="_blank">🔗 Document</a>'
    elif val.startswith("http"):
        return f'<a href="{val}" target="_blank">🔗 Document</a>'
    else:
        return f"✅ Available ({val})"

formatted_df = df.copy()
for col in formatted_df.columns[1:]:  # اولین ستون اسم سایته
    formatted_df[col] = formatted_df[col].apply(format_value)

# --- Scrollable & Centered HTML Table ---
html_table = formatted_df.to_html(escape=False, index=False)
scrollable_table = f"""
<div style="display: flex; justify-content: center; margin-top: 20px;">
  <div style="width: 90%; max-width: 1200px; height: 600px; overflow: auto; border: 1px solid #ddd; padding: 10px;">
    <style>
      table {{
        border-collapse: collapse;
        font-size: 13px;
        white-space: nowrap;
      }}
      th {{
        text-align: center !important;
        vertical-align: middle !important;
        background-color: #f2f2f2;
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
