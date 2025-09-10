from supabase import create_client
import streamlit as st
from pymongo import MongoClient




client = MongoClient("mongodb+srv://iemdpk:Imback2play@localserver.cwqbg.mongodb.net/?retryWrites=true&w=majority")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


