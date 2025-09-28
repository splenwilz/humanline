# 🚀 Humanline Vercel Deployment Checklist

## ✅ Pre-Deployment Checklist

### 1. Prerequisites
- [ ] Vercel CLI installed (`npm install -g vercel`)
- [ ] Logged into Vercel (`vercel login`)
- [ ] Neon database created and connection string ready ✅
- [ ] Upstash Redis created and connection string ready ✅

### 2. Environment Setup
- [ ] Run `./setup-vercel-env.sh` to configure Vercel environment variables
- [ ] Generate secure SECRET_KEY (32+ characters)
- [ ] Generate secure NEXTAUTH_SECRET
- [ ] Set your domain name

### 3. Database Migration
- [ ] Run `python migrate-production.py` to set up production database schema
- [ ] Verify database tables are created

### 4. Code Preparation
- [ ] Test frontend build locally (`cd frontend && npm run build`)
- [ ] Verify all dependencies are in `requirements.txt`
- [ ] Check `vercel.json` configuration

## 🚀 Deployment Steps

### 1. Configure Environment Variables
```bash
./setup-vercel-env.sh
```

### 2. Run Database Migrations
```bash
python migrate-production.py
```

### 3. Deploy to Vercel
```bash
./deploy-vercel.sh
```

## 📋 Your Database Configuration

### Neon PostgreSQL ✅
```
Database: neondb
Host: ep-lingering-meadow-admipln5-pooler.c-2.us-east-1.aws.neon.tech
Connection: Ready for production
SSL: Required (configured)
```

### Upstash Redis ✅
```
Instance: apt-hamster-13842
Host: apt-hamster-13842.upstash.io:6379
Connection: Ready for production
TLS: Enabled
```

## 🔧 Post-Deployment

### 1. Verify Deployment
- [ ] Visit your Vercel domain
- [ ] Test health endpoint: `https://your-domain.vercel.app/health`
- [ ] Test API docs: `https://your-domain.vercel.app/docs`
- [ ] Test frontend functionality

### 2. Test Authentication
- [ ] User registration
- [ ] User login
- [ ] JWT token functionality
- [ ] Protected routes

### 3. Test Database Operations
- [ ] Create operations
- [ ] Read operations
- [ ] Update operations
- [ ] Delete operations

### 4. Performance Check
- [ ] API response times
- [ ] Frontend load times
- [ ] Database query performance
- [ ] Redis caching

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### "Module not found" in Vercel Functions
- **Problem**: Python modules not found
- **Solution**: Ensure all dependencies are in `backend/requirements.txt`

#### Database Connection Errors
- **Problem**: Cannot connect to Neon database
- **Solution**: Check DATABASE_URL format and SSL requirements

#### CORS Issues
- **Problem**: Frontend can't access backend API
- **Solution**: Update ALLOWED_ORIGINS in Vercel environment variables

#### Redis Connection Issues
- **Problem**: Cannot connect to Upstash Redis
- **Solution**: Verify REDIS_URL format and TLS settings

### Environment Variables to Double-Check
```bash
# Required for functionality
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://default:...
SECRET_KEY=your-32-char-secret
NEXTAUTH_SECRET=your-nextauth-secret

# Required for frontend
NEXT_PUBLIC_API_URL=https://your-domain.vercel.app
NEXT_PUBLIC_APP_URL=https://your-domain.vercel.app
NEXTAUTH_URL=https://your-domain.vercel.app

# Required for CORS
ALLOWED_ORIGINS=https://your-domain.vercel.app
```

## 📊 Monitoring & Maintenance

### 1. Vercel Dashboard
- Monitor function execution times
- Check build logs
- Review error logs

### 2. Database Monitoring
- Neon dashboard for connection pools
- Query performance metrics
- Storage usage

### 3. Redis Monitoring
- Upstash dashboard for memory usage
- Connection statistics
- Cache hit rates

## 🎯 Performance Optimization

### 1. Database
- Use connection pooling (already configured in Neon)
- Index frequently queried columns
- Consider read replicas for heavy read workloads

### 2. Redis Caching
- Cache frequently accessed data
- Set appropriate TTL values
- Monitor cache hit rates

### 3. Vercel Optimization
- Enable edge caching where appropriate
- Optimize image delivery
- Consider Vercel Pro for better performance

## 🔐 Security Considerations

### 1. Secrets Management
- [ ] Rotate SECRET_KEY regularly
- [ ] Use strong NEXTAUTH_SECRET
- [ ] Never commit secrets to git

### 2. Database Security
- [ ] Use connection pooling
- [ ] Enable SSL (already configured)
- [ ] Monitor for unusual access patterns

### 3. API Security
- [ ] Implement rate limiting
- [ ] Validate all inputs
- [ ] Use HTTPS only (enforced by Vercel)

---

**Ready to deploy? Let's go! 🚀**

1. `./setup-vercel-env.sh`
2. `python migrate-production.py`
3. `./deploy-vercel.sh`
