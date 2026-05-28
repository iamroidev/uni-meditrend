UNIMEDITREND

---------------------------------------------------
Data Generation and Database
----------------------------

- create a connection and database on MongoDB Compass

database name		: UniMediTrend
collection name		: clinic_logs

- in jupyter notebook, run 01_data_generation ...
to populate the collection

--------------------------------------------------------
Pipeline
--------
- create a new folder and name it 'models'. This will be where all the models will be stored after running the notebook

- run notebooks 02 - 04


-----------------------------------------------------------
Dashboard
---------

- create a new folder(for the dashboard) and copy the models folder, app_.py and database.py inside

Quick start (Windows PowerShell)

1. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate

2. Install dependencies
pip install -r requirements.txt


3. Run the app
streamlit run app.py
