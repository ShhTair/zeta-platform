# 🚀 ZETA Platform - Quick Start Guide

Get the admin panel running in 5 minutes!

## ⚡ Fast Track (Local Development)

```bash
# 1. Navigate to the project
cd /path/to/zeta-platform/apps/web

# 2. Install dependencies (if not already done)
npm install

# 3. Set up environment variables
cp .env.example .env.local

# 4. Edit .env.local
# Set NEXT_PUBLIC_API_URL to your backend API URL
# Example: http://localhost:3001/api

# 5. Run development server
npm run dev

# 6. Open browser
# http://localhost:3000
```

## 🌐 Deploy to Vercel (3 minutes)

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Login to Vercel
vercel login

# 3. Deploy
cd apps/web
vercel

# 4. Set environment variable
vercel env add NEXT_PUBLIC_API_URL production
# Enter your production API URL

# 5. Deploy to production
vercel --prod
```

Done! Your app is live. ✅

## 📋 Prerequisites

- Node.js 22+ installed
- npm or yarn
- Backend API running (optional for frontend dev)
- Git (for deployment)

## 🔑 First Login

### Default Test Credentials (if backend has seed data)
```
Email: admin@zeta.com
Password: admin123
```

### Create First User
1. Visit `/register`
2. Enter details + invite code
3. Login at `/login`

## 🏗️ Project Structure

```
apps/web/
├── app/              # Pages and routes
├── components/       # Reusable components
├── lib/             # Utilities and config
├── public/          # Static files
└── .env.local       # Environment variables
```

## 🛠️ Common Commands

```bash
# Development
npm run dev          # Start dev server (port 3000)

# Production
npm run build        # Build for production
npm start            # Run production build

# Maintenance
npm run lint         # Check code quality
npx tsc --noEmit     # Type check
```

## 🔍 Troubleshooting

### "Module not found" error
```bash
rm -rf node_modules package-lock.json
npm install
```

### Build fails
```bash
rm -rf .next
npm run build
```

### API not connecting
1. Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
2. Verify backend is running
3. Check CORS settings on backend
4. Open browser console for errors

### Login not working
1. Verify backend `/auth/login` endpoint works
2. Check JWT token format
3. Clear localStorage: `localStorage.clear()`
4. Check network tab for API responses

## 📊 Test Data

To test the UI without a backend, you can mock API responses:

```typescript
// lib/api.ts - Add mock mode
const MOCK_MODE = false; // Set to true for mock data

if (MOCK_MODE) {
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.config.url.includes('/cities')) {
        return Promise.resolve({
          data: [
            { id: '1', name: 'Los Angeles', slug: 'la', isActive: true, createdAt: new Date().toISOString() },
            { id: '2', name: 'New York', slug: 'ny', isActive: true, createdAt: new Date().toISOString() },
          ]
        });
      }
      return Promise.reject(error);
    }
  );
}
```

## 🌟 Next Steps

After getting it running:

1. **Explore the UI**
   - Try all pages
   - Test responsive design (resize browser)
   - Check role-based access

2. **Customize**
   - Update colors in `tailwind.config.ts`
   - Modify logo and branding
   - Add your domain name

3. **Deploy**
   - Push to GitHub
   - Deploy on Vercel
   - Set up custom domain

4. **Monitor**
   - Enable Vercel Analytics
   - Set up error tracking
   - Monitor performance

## 📖 Documentation

- **Full README:** `README.md`
- **Deployment Guide:** `DEPLOYMENT.md`
- **Project Summary:** `PROJECT_SUMMARY.md`

## 🆘 Need Help?

1. Check browser console for errors
2. Review `README.md` for detailed setup
3. Check backend logs if API failing
4. Verify all environment variables are set
5. Test with curl: `curl -X GET http://your-api/cities`

## 💡 Tips

- **Hot Reload:** Changes automatically refresh in dev mode
- **Type Safety:** Use TypeScript for auto-completion
- **State Inspection:** React Query DevTools in bottom-left
- **Responsive Testing:** Use browser DevTools device mode

---

**Ready to build? Let's go! 🚀**

```bash
cd apps/web && npm run dev
```

Open http://localhost:3000 and start building!
