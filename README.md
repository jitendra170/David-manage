# School Management System

This Streamlit app demonstrates a school management system with role-based access for:
- Teacher
- Principal
- Accountant
- Student
- Library

## Features
- Login screen with role-specific dashboards
- Role-based task lists
- Demo authentication flow

## Run locally
1. Install dependencies:
   pip install streamlit pytest
2. Start the app:
   streamlit run app.py

## Supabase integration
Replace the demo authentication in app.py with Supabase Auth and use Supabase database tables for students, fees, library books, and school records.

### Database setup
Run the SQL in [supabase_setup.sql](supabase_setup.sql) in the Supabase SQL editor to create the table and seed demo users.
