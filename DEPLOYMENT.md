# Vercel Deployment Guide for Humanline

## 🚀 Quick Deployment Steps

### Prerequisites
1. Install Vercel CLI: `npm install -g vercel`
2. Login to Vercel: `vercel login`
3. Set up production database and Redis

### 1. Deploy to Vercel
```bash
./deploy-vercel.sh
```

### 2. Set Up Production Database

#### Option A: Neon (Recommended)
1. Go to [Neon](https://neon.tech/)
2. Create a new project
3. Copy the connection string
4. Format as: `postgresql+asyncpg://username:password@host:port/database`

#### Option B: Supabase
1. Go to [Supabase](https://supabase.com/)
2. Create a new project
3. Go to Settings > Database
4. Copy the connection string and modify for asyncpg

#### Option C: Vercel Postgres
1. In your Vercel dashboard
2. Go to Storage tab
3. Create Postgres database
4. Copy connection string

### 3. Set Up Redis

#### Option A: Upstash Redis (Recommended)
1. Go to [Upstash](https://upstash.com/)
2. Create a Redis database
3. Copy the Redis URL

#### Option B: Vercel KV
1. In your Vercel dashboard
2. Go to Storage tab
3. Create KV database
4. Copy connection details

### 4. Configure Environment Variables

In your Vercel dashboard or via CLI:

```bash
# Database
vercel env add DATABASE_URL
# Paste your database URL

# Redis
vercel env add REDIS_URL
# Paste your Redis URL

# Security (Generate strong secrets!)
vercel env add SECRET_KEY
vercel env add NEXTAUTH_SECRET

# Frontend URLs (will be your Vercel domain)
vercel env add NEXT_PUBLIC_API_URL
vercel env add NEXT_PUBLIC_APP_URL
vercel env add NEXTAUTH_URL

# CORS (add your Vercel domain)
vercel env add ALLOWED_ORIGINS
```

### 5. Environment Variables Checklist

#### Required Variables:
- [ ] `DATABASE_URL` - PostgreSQL connection string
- [ ] `REDIS_URL` - Redis connection string  
- [ ] `SECRET_KEY` - JWT secret (32+ characters)
- [ ] `NEXTAUTH_SECRET` - NextAuth secret
- [ ] `NEXT_PUBLIC_API_URL` - Your Vercel domain
- [ ] `NEXT_PUBLIC_APP_URL` - Your Vercel domain
- [ ] `NEXTAUTH_URL` - Your Vercel domain
- [ ] `ALLOWED_ORIGINS` - Your Vercel domain

#### Optional Variables:
- [ ] `SMTP_HOST` - Email service
- [ ] `SMTP_PORT` - Email port
- [ ] `SMTP_USER` - Email username
- [ ] `SMTP_PASSWORD` - Email password
- [ ] `FROM_EMAIL` - From email address

### 6. Database Migrations

After deployment, run migrations:

```bash
# Connect to your production database and run:
# You'll need to do this manually since Vercel functions are stateless

# Option 1: Run locally against production DB
DATABASE_URL="your-prod-db-url" alembic upgrade head

# Option 2: Use a migration script in Vercel function
# (Create a separate endpoint for migrations)
```

### 7. Testing Deployment

After deployment:

1. ✅ Visit your Vercel domain
2. ✅ Test API health: `https://your-domain.vercel.app/health`
3. ✅ Test API docs: `https://your-domain.vercel.app/docs`
4. ✅ Test frontend: `https://your-domain.vercel.app`
5. ✅ Test authentication flow
6. ✅ Test database operations

### 8. Custom Domain (Optional)

1. In Vercel dashboard, go to Domains
2. Add your custom domain
3. Update environment variables with new domain
4. Update CORS settings

## 🔧 Troubleshooting

### Common Issues:

#### "Module not found" errors
- Check that all dependencies are in `requirements.txt`
- Ensure Python version compatibility

#### Database connection errors
- Verify DATABASE_URL format
- Check database allows external connections
- Ensure IP allowlisting if required

#### CORS errors
- Update ALLOWED_ORIGINS environment variable
- Include both Vercel domain and custom domain

#### Cold start issues
- Consider upgrading to Vercel Pro for better performance
- Optimize imports and reduce bundle size

### Performance Tips:

1. **Enable caching**: Use Vercel's edge caching
2. **Optimize images**: Use Vercel's image optimization
3. **Database connection pooling**: Use connection pooling for database
4. **Redis caching**: Cache frequently accessed data

## 📚 Resources

- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI on Vercel](https://vercel.com/guides/deploying-fastapi-with-vercel)
- [Next.js on Vercel](https://vercel.com/docs/frameworks/nextjs)
- [Neon Database](https://neon.tech/docs)
- [Upstash Redis](https://docs.upstash.com/)
