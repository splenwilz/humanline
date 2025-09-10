#!/usr/bin/env python3
"""
Test JWT token creation and validation
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.jwt_service import jwt_service

def test_jwt():
    """Test JWT token creation and validation"""
    
    # Test user data
    user_id = "550e8400-e29b-41d4-a716-446655440000"
    email = "test@example.com"
    
    print("=== JWT Token Test ===")
    
    # Create token pair
    print("1. Creating token pair...")
    token_response = jwt_service.create_token_pair(user_id, email)
    print(f"Access Token: {token_response.access_token[:50]}...")
    print(f"Refresh Token: {token_response.refresh_token[:50]}...")
    print(f"Expires In: {token_response.expires_in} seconds")
    
    # Verify access token
    print("\n2. Verifying access token...")
    token_data = jwt_service.verify_token(token_response.access_token, "access")
    if token_data:
        print(f"✅ Access token valid")
        print(f"   User ID: {token_data.user_id}")
        print(f"   Email: {token_data.email}")
    else:
        print("❌ Access token invalid")
    
    # Verify refresh token
    print("\n3. Verifying refresh token...")
    refresh_data = jwt_service.verify_token(token_response.refresh_token, "refresh")
    if refresh_data:
        print(f"✅ Refresh token valid")
        print(f"   User ID: {refresh_data.user_id}")
        print(f"   Email: {refresh_data.email}")
    else:
        print("❌ Refresh token invalid")
    
    # Test token refresh
    print("\n4. Testing token refresh...")
    new_token = jwt_service.refresh_access_token(token_response.refresh_token)
    if new_token:
        print(f"✅ Token refresh successful")
        print(f"   New Access Token: {new_token.access_token[:50]}...")
    else:
        print("❌ Token refresh failed")
    
    print("\n=== Test Complete ===")
    return token_response.access_token

if __name__ == "__main__":
    access_token = test_jwt()
    print(f"\nUse this token for testing:")
    print(f"Authorization: Bearer {access_token}")
