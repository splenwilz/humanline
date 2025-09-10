# Humanline Backend API

A FastAPI backend with Supabase integration for authentication and user management using **OTP-only email confirmation**.

## 🚀 Features

- **User Authentication**: Signup, signin, and token refresh
- **OTP System**: One-Time Password verification for email confirmation
- **JWT Tokens**: Secure authentication with access and refresh tokens
- **Supabase Integration**: Backend-as-a-Service for database and auth
- **No Email Links**: Pure OTP-based confirmation system

## 🏗️ Architecture

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration and environment variables
│   ├── main.py            # FastAPI application entry point
│   ├── models/
│   │   └── user.py        # Pydantic models for data validation
│   ├── routers/
│   │   └── auth.py        # Authentication API endpoints
│   └── services/
│       ├── auth_service.py # Supabase authentication logic
│       └── otp_service.py # OTP generation and verification
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── start.sh               # Development server startup script
├── supabase_otp_setup.sql # SQL script for OTP table setup
├── SUPABASE_SETUP.md      # Supabase configuration guide
└── OTP_SETUP_GUIDE.md    # Complete OTP system setup guide
```

## 🛠️ Setup

### 1. **Environment Setup**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. **Environment Variables**
Copy `.env.example` to `.env` and fill in your Supabase credentials:
```bash
cp .env.example .env
```

Required variables:
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
```

### 3. **Supabase Setup**
1. Create a Supabase project
2. Run the SQL script in `supabase_otp_setup.sql` in your Supabase SQL editor
3. Configure email templates in Supabase dashboard for OTP delivery
4. **Important**: Disable email confirmation links in Supabase settings

### 4. **Start Development Server**
```bash
# Option 1: Use the startup script
./start.sh

# Option 2: Manual start
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## 📚 API Endpoints

### Authentication

#### **POST** `/api/v1/auth/signup`
Create a new user account with OTP generation.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "message": "User created successfully. Check your email for the OTP code to confirm your account.",
  "confirmation_sent": false,
  "otp_sent": true
}
```

**Features:**
- Creates user account in Supabase
- Generates and stores OTP code
- **No confirmation email sent** (OTP only)
- Returns user ID and OTP status

#### **POST** `/api/v1/auth/signin**
Authenticate existing user (email must be confirmed via OTP).

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "email_confirmed_at": "2024-01-01T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### **POST** `/api/v1/auth/verify-otp`
Verify OTP code for email confirmation.

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Note**: The email is typically retrieved from the frontend state or URL parameters, not manually entered by the user.

**Response:**
```json
{
  "message": "OTP verified successfully. Email confirmed.",
  "verified": true,
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "email_confirmed_at": "2024-01-01T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### **POST** `/api/v1/auth/resend-otp**
Generate and send a new OTP code.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "New OTP code has been sent to your email",
  "otp_sent": true
}
```

#### **POST** `/api/v1/auth/refresh**
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "your_refresh_token"
}
```

**Response:** Same as signin response with new tokens.

## 🔐 OTP System

### **How It Works**
1. **Signup**: User signs up → OTP generated and stored in database
2. **Email**: User receives email with OTP code (no confirmation links)
3. **Confirmation**: User visits `/confirm` → Enters OTP → Backend verifies
4. **Activation**: Account confirmed → User can sign in

### **OTP Features**
- **6-digit codes**: Secure random generation
- **10-minute expiry**: Automatic expiration for security
- **One-time use**: Each OTP can only be used once
- **Database storage**: Stored in Supabase with proper indexing
- **Cleanup**: Automatic cleanup of expired OTPs

### **Database Schema**
```sql
otp_codes (
  id UUID PRIMARY KEY,
  email TEXT NOT NULL,
  otp_code TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  used BOOLEAN DEFAULT FALSE
)
```

### **Security Features**
- Row Level Security (RLS) enabled
- Service role permissions for OTP operations
- Automatic cleanup of expired codes
- Rate limiting considerations (implement as needed)

## 🔧 Configuration

### **Supabase Settings**
- **Site URL**: `http://localhost:3000`
- **Redirect URLs**: **Leave empty** (no email confirmation links)
- **Email confirmations**: **Disabled** (OTP only)

### **Email Templates**
Configure in Supabase Dashboard → Authentication → Email Templates:
- **Confirm signup**: Include OTP code (not confirmation link)
- **Magic link**: Optional for alternative signin

### **CORS Configuration**
Configured for frontend at `http://localhost:3000`

## 🧪 Testing

### **Test Complete OTP Flow**
```bash
# 1. Sign up user
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "full_name": "Test User"}'

# 2. Check backend logs for OTP code
# 3. Verify OTP
curl -X POST http://localhost:8000/api/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "otp": "123456"}'

# 4. Test signin with confirmed account
curl -X POST http://localhost:8000/api/v1/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### **Test OTP Resend**
```bash
curl -X POST http://localhost:8000/api/v1/auth/resend-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

### **Test Token Refresh**
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "your_refresh_token"}'
```

## 📝 Development Notes

### **Current TODOs**
- [ ] Implement proper JWT token generation for OTP verification
- [ ] Add email service for sending OTP codes
- [ ] Implement rate limiting for OTP requests
- [ ] Add logging and monitoring
- [ ] Implement proper error handling for edge cases

### **Security Considerations**
- OTP codes expire after 10 minutes
- Each OTP can only be used once
- Database cleanup removes expired codes
- Service role required for OTP operations
- Consider implementing rate limiting

### **Performance Optimizations**
- Database indexes on email and expiry
- Automatic cleanup of expired OTPs
- Efficient OTP generation and storage

## 🚀 Production Deployment

### **Environment Variables**
- Use production Supabase credentials
- Set proper CORS origins
- Configure logging levels
- Set secure cookie settings

### **Database**
- Run OTP table setup script
- Configure automated cleanup jobs
- Monitor database performance
- Set up backups

### **Security**
- Enable HTTPS
- Set secure headers
- Implement rate limiting
- Monitor for abuse

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [OTP Security Best Practices](https://owasp.org/www-project-authentication-cheat-sheet/)

## 🤝 Contributing

1. Follow the existing code structure
2. Add proper error handling
3. Include tests for new features
4. Update documentation
5. Follow security best practices

## 🎯 Key Differences from Traditional Systems

### **Traditional Email Confirmation**
- User clicks email link
- Redirects to confirmation page
- Automatic account activation

### **Humanline OTP System**
- User receives OTP code via email
- User manually enters OTP on confirmation page
- Backend verifies OTP before activation
- **No email links or redirects**

### **Benefits of OTP-Only Approach**
- ✅ **More secure** - No clickable links in emails
- ✅ **Better UX** - Users control when to confirm
- ✅ **Mobile friendly** - Works on all devices
- ✅ **No redirect issues** - Direct page access
- ✅ **Audit trail** - OTP usage tracking
- ✅ **Rate limiting** - Prevent abuse

---

**🎉 Your Humanline backend is configured for OTP-only authentication!**
