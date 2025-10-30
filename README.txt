Bill Splitter - README

Files:
- app.py : Streamlit app
- requirements.txt : Python dependencies

Quick start (local):
1. Create a virtual environment (optional but recommended)
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # mac / linux:
   source .venv/bin/activate

2. Install dependencies:
   pip install -r requirements.txt

3. Run the app:
   streamlit run app.py

Notes:
- Use the sidebar button to toggle Light / Dark theme.
- Add participants using the 'Participant name' form. After adding each participant, expand their card to add items.
- You can input Tax and Service as percentage of the bill or as fixed amounts.
- If no item prices are entered, the app falls back to equal split.

Deploy:
- Streamlit Cloud: push this repo to GitHub and connect to https://share.streamlit.io
- Hugging Face Spaces: create a new Space with Streamlit runtime and upload these files.

Enjoy!
