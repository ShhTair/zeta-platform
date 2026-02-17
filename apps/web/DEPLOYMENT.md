# ZETA Platform - Deployment Guide

## 🚀 Quick Deploy to Vercel

### Prerequisites
- GitHub account
- Vercel account (free tier works)
- Backend API running (required for full functionality)

### Steps

#### 1. Push to GitHub

```bash
cd /path/to/zeta-platform
git init
git add .
git commit -m "Initial commit: ZETA Platform admin panel"
git remote add origin https://github.com/yourusername/zeta-platform.git
git push -u origin main
```

#### 2. Deploy to Vercel

**Option A: Via Vercel Dashboard**
1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import your GitHub repository
4. Vercel will auto-detect Next.js
5. Set Root Directory to: `apps/web`
6. Add Environment Variable:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://your-api-domain.com/api`
7. Click "Deploy"

**Option B: Via Vercel CLI**
```bash
npm i -g vercel
cd apps/web
vercel

# Follow the prompts:
# - Link to existing project? N
# - Project name: zeta-platform-web
# - Directory: ./
# - Override settings? N

# Set environment variable:
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://your-api-domain.com/api

# Deploy to production:
vercel --prod
```

#### 3. Configure Custom Domain (Optional)

1. In Vercel Dashboard → Project Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions
4. Wait for SSL certificate provisioning (~5 minutes)

## 🔧 Environment Variables

### Production Environment

Set these in your Vercel project settings:

```env
NEXT_PUBLIC_API_URL=https://api.zetaplatform.com/api
```

### Staging Environment (Optional)

```env
NEXT_PUBLIC_API_URL=https://staging-api.zetaplatform.com/api
```

## 🏗️ Manual Deployment (VPS/Custom Server)

### Using PM2 (Recommended)

```bash
# Install PM2
npm install -g pm2

# Build the application
cd apps/web
npm run build

# Start with PM2
pm2 start npm --name "zeta-web" -- start

# Configure PM2 to restart on reboot
pm2 startup
pm2 save
```

### Using Docker

```dockerfile
# Dockerfile
FROM node:22-alpine AS base

FROM base AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000

CMD ["node", "server.js"]
```

Build and run:
```bash
docker build -t zeta-web .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=https://your-api.com/api zeta-web
```

### Using Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/zeta-platform
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/zeta-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Add SSL with Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 🔄 CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '22'
          cache: 'npm'
          cache-dependency-path: 'apps/web/package-lock.json'
      
      - name: Install dependencies
        working-directory: ./apps/web
        run: npm ci
      
      - name: Type check
        working-directory: ./apps/web
        run: npx tsc --noEmit
      
      - name: Lint
        working-directory: ./apps/web
        run: npm run lint
      
      - name: Build
        working-directory: ./apps/web
        run: npm run build
        env:
          NEXT_PUBLIC_API_URL: ${{ secrets.NEXT_PUBLIC_API_URL }}
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./apps/web
```

## 🔍 Health Checks

### Endpoint Monitoring

Monitor these endpoints:
- `https://your-domain.com/` - Should redirect to login or dashboard
- `https://your-domain.com/login` - Login page should load
- API connectivity through the app

### Recommended Monitoring Tools
- [Vercel Analytics](https://vercel.com/analytics) (built-in)
- [UptimeRobot](https://uptimerobot.com)
- [Pingdom](https://www.pingdom.com)
- [Better Stack](https://betterstack.com)

## 🐛 Troubleshooting

### Build Failures

**Issue:** `Module not found` errors
```bash
cd apps/web
rm -rf node_modules package-lock.json .next
npm install
npm run build
```

**Issue:** TypeScript errors
```bash
npx tsc --noEmit
# Fix reported errors
```

### Runtime Issues

**Issue:** API requests failing (CORS)
- Ensure backend has correct CORS configuration
- Check `NEXT_PUBLIC_API_URL` environment variable
- Verify API is accessible from client browser

**Issue:** Authentication not persisting
- Check browser localStorage is enabled
- Verify JWT token format and expiration
- Check browser console for errors

**Issue:** 404 on page refresh
- Ensure your hosting supports SPA routing
- For Nginx, add `try_files` directive
- Vercel handles this automatically

### Performance Issues

**Check these:**
1. Enable caching headers
2. Optimize images (use Next.js Image component)
3. Analyze bundle size: `npm run build` shows bundle analysis
4. Enable compression in your hosting

## 📊 Analytics & Monitoring

### Vercel Analytics (Recommended)

Already integrated! Just enable in Vercel dashboard.

### Google Analytics

Add to `app/layout.tsx`:

```typescript
import Script from 'next/script'

export default function RootLayout({ children }) {
  return (
    <html>
      <head>
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"
          strategy="afterInteractive"
        />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'GA_MEASUREMENT_ID');
          `}
        </Script>
      </head>
      <body>{children}</body>
    </html>
  )
}
```

## 🔐 Security Checklist

Before deploying to production:

- [ ] Environment variables set correctly (no secrets in code)
- [ ] HTTPS enabled (SSL certificate)
- [ ] Content Security Policy configured
- [ ] Rate limiting on API
- [ ] JWT token expiration configured
- [ ] Sensitive routes protected with authentication
- [ ] XSS protection enabled
- [ ] CSRF protection on forms
- [ ] Regular dependency updates (`npm audit`)

## 🔄 Update Strategy

### Rolling Updates

```bash
# Pull latest changes
git pull origin main

# Install any new dependencies
npm install

# Build new version
npm run build

# Restart application (PM2 example)
pm2 restart zeta-web
```

### Zero-Downtime with Vercel

Vercel automatically provides zero-downtime deployments:
1. New version is built
2. Preview deployment created
3. After passing checks, traffic switches atomically
4. Old version kept for instant rollback

### Rollback

**Vercel:**
Dashboard → Deployments → Click previous deployment → "Promote to Production"

**PM2:**
```bash
pm2 start ecosystem.config.js --env production
pm2 reload zeta-web
```

## 📈 Scaling

### Horizontal Scaling (Vercel)
- Automatically scales based on traffic
- No configuration needed
- Supports unlimited concurrent users

### Custom Infrastructure
- Use load balancer (Nginx, HAProxy)
- Run multiple Next.js instances
- Use Redis for session storage
- CDN for static assets (Cloudflare, AWS CloudFront)

## 💰 Cost Estimates

### Vercel (Recommended)
- **Hobby (Free):** Perfect for development/small teams
- **Pro ($20/month):** Production use, custom domains, analytics
- **Enterprise:** Custom pricing for large scale

### Self-Hosted VPS
- **DigitalOcean Droplet:** $12/month (2GB RAM, 2vCPU)
- **AWS Lightsail:** $10/month (2GB RAM, 1vCPU)
- **Linode:** $12/month (2GB RAM, 2vCPU)

---

## 🆘 Support

For deployment issues:
1. Check build logs in Vercel dashboard
2. Review browser console for errors
3. Verify environment variables
4. Check API connectivity
5. Contact development team

Happy deploying! 🚀
