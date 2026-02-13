#!/bin/bash

# Lean Landing Page Deployment Script
# Supports Vercel, Netlify, and GitHub Pages

set -e

echo "🚀 Lean Landing Page Deployment"
echo "================================"
echo ""

# Check current directory
if [ ! -f "index.html" ]; then
    echo "❌ Error: index.html not found. Run this script from the landing/ directory."
    exit 1
fi

echo "Choose deployment platform:"
echo "1) Vercel (recommended)"
echo "2) Netlify"
echo "3) GitHub Pages"
echo "4) Local preview"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🟢 Deploying to Vercel..."
        echo ""
        if ! command -v vercel &> /dev/null; then
            echo "Installing Vercel CLI..."
            npm install -g vercel
        fi
        
        echo "Note: You'll need to authenticate with Vercel"
        echo "Run: vercel login"
        echo "Then run: vercel --prod"
        echo ""
        read -p "Press enter to run vercel login..."
        vercel login
        
        echo ""
        echo "Deploying..."
        vercel --prod
        ;;
    2)
        echo ""
        echo "🔵 Deploying to Netlify..."
        echo ""
        if ! command -v netlify &> /dev/null; then
            echo "Installing Netlify CLI..."
            npm install -g netlify-cli
        fi
        
        echo "Note: You'll need to authenticate with Netlify"
        netlify login
        
        echo ""
        echo "Deploying..."
        netlify deploy --prod --dir=.
        ;;
    3)
        echo ""
        echo "🟣 Setting up for GitHub Pages..."
        echo ""
        read -p "Enter your GitHub username: " github_user
        read -p "Enter repository name (default: lean-landing): " repo_name
        repo_name=${repo_name:-lean-landing}
        
        if [ ! -d ".git" ]; then
            git init
            git add .
            git commit -m "Initial landing page"
            git branch -M main
            git remote add origin "https://github.com/$github_user/$repo_name.git"
        fi
        
        echo ""
        echo "Pushing to GitHub..."
        git push -u origin main
        
        echo ""
        echo "✅ Pushed to GitHub!"
        echo "Now enable GitHub Pages:"
        echo "1. Go to https://github.com/$github_user/$repo_name/settings/pages"
        echo "2. Set Source to 'Deploy from branch: main'"
        echo "3. Your site will be at: https://$github_user.github.io/$repo_name/"
        ;;
    4)
        echo ""
        echo "🟡 Starting local preview..."
        echo ""
        if command -v python3 &> /dev/null; then
            echo "Server running at: http://localhost:8000"
            echo "Press Ctrl+C to stop"
            echo ""
            python3 -m http.server 8000
        elif command -v python &> /dev/null; then
            echo "Server running at: http://localhost:8000"
            echo "Press Ctrl+C to stop"
            echo ""
            python -m SimpleHTTPServer 8000
        else
            echo "Opening index.html in browser..."
            open index.html 2>/dev/null || xdg-open index.html 2>/dev/null || echo "Please open index.html manually"
        fi
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Done!"
