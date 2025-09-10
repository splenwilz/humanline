# Humanline - HR Management Platform

A modern, full-stack HR management platform built with Next.js, FastAPI, and Supabase. Humanline provides comprehensive tools for employee onboarding, company management, and HR operations.

## 🚀 Features

### Authentication & Security
- **Email-based OTP Authentication** - Secure signup and login with one-time passwords
- **JWT Token Management** - Automatic token refresh and secure API access
- **Supabase Integration** - Enterprise-grade authentication and database services

### Onboarding System
- **Multi-step Onboarding Flow** - Guided company setup process
- **Real-time Domain Validation** - Instant feedback on company domain availability
- **Form Auto-save** - Never lose progress with automatic form state management
- **Company Profile Setup** - Complete company information collection

### User Experience
- **Modern UI/UX** - Built with Shadcn/ui components and Tailwind CSS
- **Type-safe Development** - Full TypeScript implementation
- **Responsive Design** - Works seamlessly across all devices
- **Real-time Feedback** - Toast notifications and loading states

## 🛠️ Tech Stack

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Shadcn/ui** - Modern component library
- **SWR** - Data fetching and caching
- **React Hook Form** - Form management
- **Zod** - Schema validation

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation and serialization
- **Supabase** - Backend-as-a-Service
- **JWT** - Token-based authentication
- **SQLAlchemy** - Database ORM

### Database
- **Supabase PostgreSQL** - Managed PostgreSQL database
- **Row Level Security** - Fine-grained access control

## 📁 Project Structure

```
humanline/
├── frontend/                 # Next.js frontend application
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   ├── components/      # Reusable UI components
│   │   ├── contexts/        # React contexts
│   │   ├── data/           # API client and hooks
│   │   ├── hooks/          # Custom React hooks
│   │   └── lib/            # Utility functions
│   └── public/             # Static assets
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── models/         # Pydantic models
│   │   ├── routers/        # API route handlers
│   │   ├── services/       # Business logic
│   │   └── dependencies/   # FastAPI dependencies
│   └── sql/               # Database scripts
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Supabase account

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/splenwilz/humanline.git
   cd humanline
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**
   
   Create `.env` files in both frontend and backend directories:
   
   **Backend `.env`:**
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_KEY=your_supabase_service_key
   JWT_SECRET_KEY=your_jwt_secret_key
   DEBUG=true
   ```
   
   **Frontend `.env.local`:**
   ```env
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

5. **Database Setup**
   
   Run the SQL scripts in `backend/sql/` to set up your Supabase database:
   - `create_onboarding_table.sql`
   - `fix_onboarding_rls_policies.sql`

6. **Start the Development Servers**
   
   **Backend:**
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```
   
   **Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

7. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📖 API Documentation

The API documentation is automatically generated and available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `POST /api/v1/auth/signup` - User registration
- `POST /api/v1/auth/verify-otp` - Email verification
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/onboarding` - Submit onboarding data
- `GET /api/v1/onboarding` - Get onboarding status
- `GET /api/v1/onboarding/check-domain` - Check domain availability

## 🔧 Development

### Code Quality
- **TypeScript** - Strict type checking enabled
- **ESLint** - Code linting and formatting
- **Prettier** - Code formatting
- **Husky** - Git hooks for quality checks


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Development Team** - Full-stack development
- **Design Team** - UI/UX design
- **DevOps Team** - Infrastructure and deployment

## 📞 Support

For support, email support@tasknify.com or join our Slack channel.

## 🔮 Roadmap

- [ ] Employee management system
- [ ] Time tracking and attendance
- [ ] Performance management
- [ ] Payroll integration
- [ ] Mobile application
- [ ] Advanced analytics dashboard

---

**Humanline** - Streamlining HR operations for modern businesses.