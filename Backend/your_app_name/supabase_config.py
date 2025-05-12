from supabase import create_client, Client

SUPABASE_URL = "https://emcolberdmygupfchqtf.supabase.co" # Replace with your Supabase URL
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVtY29sYmVyZG15Z3VwZmNocXRmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA1Njc3MjIsImV4cCI6MjA1NjE0MzcyMn0.8LxWBOCFhxomqE6GsVP5ud9Ig6fUUTFU1cVU-hbN23Q"  # Replace with your Supabase API key

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)