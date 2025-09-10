#!/usr/bin/env python3
"""
Test script to verify Supabase connection and permissions
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test Supabase connection with different keys"""
    
    supabase_url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    print(f"Supabase URL: {supabase_url}")
    print(f"Anon Key: {'✅ Set' if anon_key else '❌ Missing'}")
    print(f"Service Key: {'✅ Set' if service_key else '❌ Missing'}")
    
    if not supabase_url or not anon_key:
        print("❌ Missing required environment variables")
        return
    
    # Test with anon key
    print("\n--- Testing with Anon Key ---")
    try:
        anon_client = create_client(supabase_url, anon_key)
        result = anon_client.table("onboarding").select("count").execute()
        print(f"✅ Anon key connection successful: {len(result.data)} records")
    except Exception as e:
        print(f"❌ Anon key connection failed: {e}")
    
    # Test with service key (if available)
    if service_key:
        print("\n--- Testing with Service Key ---")
        try:
            service_client = create_client(supabase_url, service_key)
            result = service_client.table("onboarding").select("count").execute()
            print(f"✅ Service key connection successful: {len(result.data)} records")
        except Exception as e:
            print(f"❌ Service key connection failed: {e}")
    else:
        print("\n⚠️  Service key not set - using anon key for database operations")

if __name__ == "__main__":
    test_connection()
