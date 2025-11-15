#!/bin/bash

# WorkExperio Render Deployment Helper Script
# This script helps prepare and deploy to Render

echo "🚀 WorkExperio - Render Deployment Helper"
echo "=========================================="
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "⚠️  Git repository not found. Initializing..."
    git init
    echo "✅ Git initialized"
fi

# Check if code is committed
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  You have uncommitted changes."
    read -p "Do you want to commit them now? (y/n): " commit_choice
    if [ "$commit_choice" = "y" ]; then
        git add .
        read -p "Enter commit message: " commit_msg
        git commit -m "${commit_msg:-Ready for deployment}"
        echo "✅ Changes committed"
    fi
fi

# Check if remote exists
if ! git remote | grep -q origin; then
    echo "⚠️  No GitHub remote found."
    read -p "Enter your GitHub repository URL: " repo_url
    git remote add origin "$repo_url"
    echo "✅ Remote added"
fi

# Push to GitHub
echo ""
echo "📤 Pushing to GitHub..."
read -p "Do you want to push to GitHub now? (y/n): " push_choice
if [ "$push_choice" = "y" ]; then
    git push -u origin main || git push -u origin master
    echo "✅ Pushed to GitHub"
fi

echo ""
echo "✅ Preparation complete!"
echo ""
echo "Next steps:"
echo "1. Go to https://dashboard.render.com"
echo "2. Follow the steps in RENDER_DEPLOY.md"
echo ""
echo "Or use the quick deploy:"
echo "1. Create PostgreSQL database"
echo "2. Create Web Service (backend)"
echo "3. Create Static Site (frontend)"
echo "4. Initialize database using Shell"
echo ""
echo "See RENDER_DEPLOY.md for detailed instructions."

