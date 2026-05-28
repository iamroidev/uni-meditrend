import pandas as pd
from pymongo import MongoClient
import streamlit as st

@st.cache_data(ttl=600)
def load_data():
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['UniMediTrend'] 
    
    # Read the enriched data from Phase 3/4
    collection = db['clinic_logs_enriched']
    
    # Fetch data, excluding the MongoDB internal '_id'
    data = list(collection.find({}, {'_id': 0}))
    df = pd.DataFrame(data)
    
    # Ensure our dates are strictly datetime objects
    if 'visit_date' in df.columns:
        df['visit_date'] = pd.to_datetime(df['visit_date'])
        
        # --- THE FIX: Recreate the time-series columns from Phase 4 ---
        df['week'] = df['visit_date'].dt.isocalendar().week.astype(int)
        df['year'] = df['visit_date'].dt.isocalendar().year.astype(int)
        
    return df

def insert_new_visit(record_dict):
    """Inserts a new clinic visit into MongoDB and clears the app cache."""
    client = MongoClient('mongodb://localhost:27017/')
    db = client['UniMediTrend'] 
    collection = db['clinic_logs_enriched']
    
    # Insert the record
    collection.insert_one(record_dict)
    
    # CRITICAL: Clear the cache so Streamlit knows to fetch the new data!
    st.cache_data.clear()