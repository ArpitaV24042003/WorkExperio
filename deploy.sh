#!/bin/bash

# WorkExperio Deployment Script
# This script helps deploy to various platforms

echo "🚀 WorkExperio Deployment Helper"
echo "================================"
echo ""
echo "Choose deployment platform:"
echo "1) Render (Recommended - Easy)"
echo "2) Railway"
echo "3) Docker Compose (Local/Server)"
echo "4) Vercel (Frontend only)"
echo "5) Manual deployment guide"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
  1)
    echo ""
    echo "📋 Render Deployment Steps:"
    echo "1. Push render.yaml to GitHub"
    echo "2. Go to render.com and connect your repo"
    echo "3. Render will auto-detect render.yaml"
    echo "4. Add environment variables in Render dashboard"
    echo "5. Deploy!"
    echo ""
    echo "See DEPLOY_QUICK.md for detailed steps"
    ;;
  2)
    echo ""
    echo "📋 Railway Deployment:"
    echo "1. Install Railway CLI: npm i -g @railway/cli"
    echo "2. Run: railway login"
    echo "3. Run: railway init"
    echo "4. Run: railway up"
    echo ""
    ;;
  3)
    echo ""
    echo "🐳 Docker Compose Deployment:"
    echo "1. Update environment variables in docker-compose.yml"
    echo "2. Run: docker-compose up -d"
    echo ""
    ;;
  4)
    echo ""
    echo "📋 Vercel Frontend Deployment:"
    echo "1. cd frontend"
    echo "2. npm install -g vercel"
    echo "3. vercel --prod"
    echo ""
    ;;
  5)
    echo ""
    echo "📚 See DEPLOYMENT_GUIDE.md for complete instructions"
    ;;
  *)
    echo "Invalid choice"
    ;;
esac


