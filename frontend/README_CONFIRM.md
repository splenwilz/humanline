# Frontend Email Confirmation Page

## 🎯 Purpose

This page handles **OTP (One-Time Password) verification** for email confirmation. Users enter the 6-digit OTP code sent to their email to confirm their account.

**Note**: This system uses **OTP codes ONLY** - no email confirmation links are used, and users don't need to enter their email again.

## 🔄 How It Works

### **User Flow**

```
User signs up → Email sent with OTP code → User visits /confirm → Enters 6-digit OTP → Verification → Account confirmed
```

### **What Happens**

1. **User visits** `/confirm` page
2. **OTP form displayed** with OTP input field only
3. **User enters** the 6-digit OTP code from their email
4. **Backend verifies** the OTP code
5. **Account confirmed** and tokens stored
6. **Success page** shown with next steps

## 🛠️ Features

### **OTP Code Verification**

- **No email input required** - Email is retrieved from URL params or stored during signup
- 6-digit OTP code input field
- Form validation with error messages
- Loading states during verification
- Resend OTP functionality

### **User Experience**

- Clean, modern UI design
- Responsive layout for all devices
- Clear error messages and feedback
- Loading indicators during API calls
- Toast notifications for success/error
- Shows which email the OTP was sent to

### **Security Features**

- Form validation with Zod schema
- Secure API communication
- Token storage in localStorage
- User profile management

## 📱 UI Components Used

- **Button** - From your UI components
- **Input** - For OTP code entry only
- **Label** - Form labels
- **Icons** - Lucide React (CheckCircle, XCircle, Loader2, Key)
- **Toast notifications** - Sonner for success/error messages

## 🔐 Token Management

### **Stored in localStorage**

- `access_token` - For API calls
- `refresh_token` - For getting new tokens
- `token_expires_in` - Token expiration
- `user_profile` - User information

### **Utility Functions**

Uses `@/lib/auth` for:

- `storeTokens()` - Save authentication tokens
- `storeUserProfile()` - Save user information

## 🚀 Next Steps

After confirmation, users can:

1. **Sign In** - Go to `/signin` page
2. **Go Home** - Return to homepage
3. **Use API** - Tokens are ready for backend calls

## 🔧 Configuration

### **Backend API**

The OTP verification requires these backend endpoints:

```
POST /api/v1/auth/verify-otp
Body: { "email": "user@example.com", "otp": "123456" }

POST /api/v1/auth/resend-otp
Body: { "email": "user@example.com" }
```

### **Frontend Routes**

Ensure these routes exist:

- `/confirm` - This confirmation page
- `/signin` - Sign in page
- `/` - Homepage

## 🎨 Customization

### **Colors**

- OTP Form: Purple gradient background
- Success: Green gradient background
- Error: Red gradient background

### **Messages**

- Update text in the component
- Modify button labels
- Change navigation routes

### **Styling**

- Uses Tailwind CSS classes
- Responsive design
- Mobile-friendly layout

## 🧪 Testing

### **Test OTP Confirmation**

1. Start your frontend: `npm run dev`
2. Visit `/confirm` directly
3. Should show OTP input form (no email field)
4. Enter test OTP code
5. Test validation and error handling

### **Test Error Cases**

- Test with invalid OTP format
- Test with expired OTP codes
- Test network errors
- Test without email in URL params

### **Test Success Flow**

- Enter valid OTP
- Verify account confirmation
- Check token storage
- Test navigation to signin

## 📝 Notes

- **OTP-only**: No email confirmation links supported
- **No email input**: Email is retrieved automatically
- **Form validation**: Zod schema ensures data quality
- **API integration**: Calls backend for OTP verification
- **Secure storage**: Tokens stored in localStorage (consider httpOnly cookies for production)
- **User feedback**: Toast notifications for all states
- **Responsive design**: Works on all device sizes

## 🔍 Technical Details

### **Form Handling**

```typescript
// Form validation with Zod (email not required)
const OTPFormSchema = z.object({
  otp: z.string().min(6).max(6),
})

// Form submission
const handleOTPSubmit = async (data: z.infer<typeof OTPFormSchema>) => {
  // Email is retrieved from state/URL params
  const response = await fetch('http://localhost:8000/api/v1/auth/verify-otp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: userEmail, otp: data.otp }),
  })
}
```

### **Email Retrieval**

- **URL Parameters**: `?email=user@example.com`
- **State Management**: Email stored during signup flow
- **Fallback**: Redirect to signup if email not found

### **State Management**

- `status` - Tracks confirmation status (loading, success, error)
- `isProcessingOTP` - Shows loading state during verification
- `userEmail` - Stores email for OTP verification
- Form state managed by `react-hook-form`

### **Error Handling**

- API errors displayed as toast notifications
- Form validation errors shown inline
- Network errors handled gracefully
- User-friendly error messages

## 🚨 Troubleshooting

### **Common Issues**

#### **Form Not Showing**

- Check if all dependencies are installed
- Verify component imports are correct
- Check browser console for errors

#### **OTP Verification Fails**

- Verify backend is running
- Check API endpoint URL
- Verify OTP code is correct
- Check backend logs for errors
- Ensure email is available in state

#### **Tokens Not Stored**

- Check localStorage permissions
- Verify auth utility functions
- Check browser console for errors

### **Debug Steps**

1. Check browser console for errors
2. Verify backend API is accessible
3. Test API endpoints with curl
4. Check network tab for failed requests
5. Verify environment variables
6. Check if email is being passed correctly

## 📚 Dependencies

### **Required Packages**

```json
{
  "@hookform/resolvers": "^3.0.0",
  "react-hook-form": "^7.0.0",
  "zod": "^3.0.0",
  "sonner": "^1.0.0",
  "lucide-react": "^0.300.0"
}
```

### **Installation**

```bash
npm install @hookform/resolvers react-hook-form zod sonner lucide-react
```

## 🎯 Summary

This confirmation page provides a **streamlined OTP verification experience**:

✅ **OTP-only confirmation** - No email links  
✅ **No email input** - Email retrieved automatically  
✅ **Beautiful UI** - Modern, responsive design  
✅ **Form validation** - Zod schema validation  
✅ **Error handling** - User-friendly error messages  
✅ **Token management** - Secure storage and retrieval  
✅ **Navigation** - Clear next steps for users

**Ready to use!** Users will have a professional, secure way to confirm their accounts using just the OTP code from their email.
