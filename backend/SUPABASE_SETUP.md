# Supabase Setup Guide for Humanline

This guide will help you configure Supabase for the Humanline project with **OTP-based email confirmation**.

## 🎯 Overview

Humanline uses **Supabase's built-in OTP system** for email confirmation. Users will:
1. Sign up with email/password
2. Receive an OTP code via email from Supabase
3. Enter the OTP code to confirm their account
4. Sign in with their credentials

**We use Supabase's OTP system** - no custom OTP generation needed!

## 🚀 Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click **"Start your project"**
3. Sign in with GitHub or Google
4. Click **"New project"**
5. Choose your organization
6. Enter project details:
   - **Name**: `humanline` (or your preferred name)
   - **Database Password**: Generate a strong password
   - **Region**: Choose closest to your users
7. Click **"Create new project"**
8. Wait for project setup (2-3 minutes)

## ⚙️ Step 2: Configure Authentication Settings

### **2.1 Email Auth Provider**

1. Go to **Authentication** → **Providers**
2. Ensure **Email** is enabled
3. Configure email settings:
   - **Enable email confirmations**: ✅ **ENABLED** (we use Supabase's OTP)
   - **Enable secure email change**: ✅ **ENABLED**
   - **Enable double confirm changes**: ✅ **ENABLED**

### **2.2 Site URL Configuration**

1. Go to **Authentication** → **URL Configuration**
2. Set **Site URL** to: `http://localhost:3000`
3. **Leave Redirect URLs empty** (we don't use email confirmation links)

### **2.3 Email Templates**

1. Go to **Authentication** → **Email Templates**
2. **Confirm signup** template:
   - **Subject**: `Confirm your Humanline account`
   - **Content**: 
   ```
   Welcome to Humanline!
   
   Your account has been created successfully.
   
   To confirm your account, please use the OTP code: {{ .Token }}
   
   This code will expire in 10 minutes.
   
   If you didn't create this account, please ignore this email.
   
   Best regards,
   The Humanline Team
   ```

3. **Magic link** template (optional):
   - **Subject**: `Sign in to Humanline`
   - **Content**: 
   ```
   Hello!
   
   Click the link below to sign in to your Humanline account:
   
   {{ .ConfirmationURL }}
   
   This link will expire in 1 hour.
   
   If you didn't request this, please ignore this email.
   
   Best regards,
   The Humanline Team
   ```

## 🗄️ Step 3: Database Setup

### **3.1 Get Database Credentials**

1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL**: `https://your-project-id.supabase.co`
   - **Anon public key**: `eyJ...` (starts with eyJ)
   - **Service role key**: `eyJ...` (starts with eyJ)

### **3.2 Update Environment Variables**

In your backend `.env` file:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
```

## 🔐 Step 4: Security Configuration

### **4.1 Row Level Security (RLS)**

RLS is enabled by default in Supabase. Your OTP verification will work with the service role key.

### **4.2 API Keys**

- **Anon Key**: Used for public operations (signup, signin)
- **Service Key**: Used for admin operations (OTP verification, user lookup)

## 📧 Step 5: Email Configuration

### **5.1 SMTP Settings (Optional)**

If you want to use your own SMTP server instead of Supabase's default:

1. Go to **Settings** → **SMTP**
2. Configure your SMTP server:
   - **Host**: smtp.gmail.com (or your provider)
   - **Port**: 587
   - **Username**: your-email@gmail.com
   - **Password**: your-app-password
   - **Sender Email**: noreply@yourdomain.com

### **5.2 Test Email Sending**

1. Go to **Authentication** → **Users**
2. Create a test user
3. Check if confirmation email is sent
4. Verify OTP code is received

## 🔒 Step 6: Security Configuration

### **6.1 Password Policies**

1. Go to **Authentication** → **Settings**
2. Configure password requirements:
   - **Minimum length**: 8 characters
   - **Require numbers**: ✅ Enabled
   - **Require special characters**: ✅ Enabled

### **6.2 Session Management**

1. **JWT expiry**: 1 hour (default)
2. **Refresh token expiry**: 1 year (default)

## 🧪 Step 7: Testing

### **7.1 Test Complete OTP Flow**

```bash
# 1. Sign up user
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "full_name": "Test User"}'

# 2. Check email for OTP code
# 3. Verify OTP
curl -X POST http://localhost:8000/api/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "otp": "123456"}'

# 4. Test signin with confirmed account
curl -X POST http://localhost:8000/api/v1/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### **7.2 Test OTP Resend**

```bash
curl -X POST http://localhost:8000/api/v1/auth/resend-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

### **7.3 Test Frontend**

1. Visit `http://localhost:3000/confirm?email=test@example.com`
2. Enter OTP code from email
3. Verify account confirmation works

## 🚨 Step 8: Common Issues & Solutions

### **8.1 OTP Not Received**

**Problem**: Users not receiving OTP emails
**Solution**:
- Check spam folder
- Verify email template configuration
- Check SMTP settings if using custom server
- Ensure email confirmations are enabled

### **8.2 OTP Verification Fails**

**Problem**: OTP verification not working
**Solution**:
- Verify OTP code is correct
- Check if OTP has expired
- Ensure backend is using correct Supabase credentials
- Check backend logs for errors

### **8.3 Email Not Sent**

**Problem**: Users not receiving OTP emails
**Solution**:
- Check SMTP configuration
- Verify email templates
- Check spam folders
- Test with different email providers

## 📊 Step 9: Monitoring

### **9.1 User Confirmation Status**

```sql
-- Check unconfirmed users
SELECT 
    u.email,
    u.created_at,
    u.email_confirmed_at
FROM auth.users u
WHERE u.email_confirmed_at IS NULL
ORDER BY u.created_at DESC;
```

### **9.2 Email Delivery Status**

Check Supabase dashboard → **Authentication** → **Users** for email status.

## 🚀 Step 10: Production Deployment

### **10.1 Environment Variables**

Update your production environment:
```env
SUPABASE_URL=https://your-production-project.supabase.co
SUPABASE_ANON_KEY=your-production-anon-key
SUPABASE_SERVICE_KEY=your-production-service-key
```

### **10.2 Site URL Updates**

Update Supabase settings for production:
- **Site URL**: `https://yourdomain.com`
- **Redirect URLs**: Leave empty (OTP-only)

### **10.3 Email Templates**

Update email templates for production:
- Use your domain in sender email
- Update branding and messaging
- Test with production email service

## 📚 Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Auth Guide](https://supabase.com/docs/guides/auth)
- [Supabase Database Guide](https://supabase.com/docs/guides/database)
- [Supabase Email Templates](https://supabase.com/docs/guides/auth/auth-email-templates)

## 🎯 Summary

Your Supabase project is now configured for **OTP-based email confirmation**:

✅ **Authentication**: Email/password signup  
✅ **Confirmation**: Supabase OTP system  
✅ **Email**: Templates configured for OTP delivery  
✅ **Security**: RLS enabled, service role configured  
✅ **Integration**: Backend uses Supabase's OTP verification  

**Next Steps:**
1. Test the complete OTP flow
2. Verify email delivery works
3. Test frontend integration
4. Monitor user confirmation rates

---

**🎉 Your Supabase project is ready for OTP-based authentication!**
