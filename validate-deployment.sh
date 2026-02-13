#!/bin/bash
# GitHub Pages Deployment Validation Script
# This script validates that all files are in place for GitHub Pages deployment

set -e

echo "================================================"
echo "GitHub Pages Deployment Validation"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} Found: $1"
        return 0
    else
        echo -e "${RED}✗${NC} Missing: $1"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

# Function to check directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} Found directory: $1"
        return 0
    else
        echo -e "${RED}✗${NC} Missing directory: $1"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

# Function to check file contains pattern
check_content() {
    if grep -q "$2" "$1" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Content verified in: $1"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} Warning: Expected content not found in $1"
        WARNINGS=$((WARNINGS + 1))
        return 1
    fi
}

echo "=== Checking Documentation Files ==="
echo ""

check_dir "docs"
check_file "docs/index.html"
check_file "docs/setup.html"
check_file "docs/api.html"
check_file "docs/styles.css"
check_file "docs/README.md"
check_file "docs/.nojekyll"

echo ""
echo "=== Checking Workflow Files ==="
echo ""

check_dir ".github/workflows"
check_file ".github/workflows/deploy-pages.yml"

echo ""
echo "=== Checking Documentation Files ==="
echo ""

check_file "GITHUB_PAGES_SETUP.md"
check_file "SECURITY.md"
check_file "README.md"

echo ""
echo "=== Validating Workflow Configuration ==="
echo ""

if [ -f ".github/workflows/deploy-pages.yml" ]; then
    check_content ".github/workflows/deploy-pages.yml" "deploy-pages"
    check_content ".github/workflows/deploy-pages.yml" "github-pages"
    check_content ".github/workflows/deploy-pages.yml" "permissions:"
    check_content ".github/workflows/deploy-pages.yml" "./docs"
fi

echo ""
echo "=== Validating HTML Structure ==="
echo ""

if [ -f "docs/index.html" ]; then
    check_content "docs/index.html" "<!DOCTYPE html>"
    check_content "docs/index.html" "styles.css"
    check_content "docs/index.html" "GenAI Summarizer"
fi

echo ""
echo "=== Checking for Security Issues ==="
echo ""

# Check for accidentally committed secrets
if grep -r "AZURE_OPENAI_API_KEY.*=.*[A-Za-z0-9]" docs/ 2>/dev/null | grep -v "your_api_key_here" | grep -v "YOUR_"; then
    echo -e "${RED}✗${NC} WARNING: Potential API key found in docs/"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓${NC} No API keys found in documentation"
fi

if grep -r "SECRET_KEY.*=.*[A-Za-z0-9]" docs/ 2>/dev/null | grep -v "your_secret_key" | grep -v "YOUR_"; then
    echo -e "${RED}✗${NC} WARNING: Potential secret key found in docs/"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓${NC} No secret keys found in documentation"
fi

# Check .env is not in docs
if [ -f "docs/.env" ]; then
    echo -e "${RED}✗${NC} ERROR: .env file found in docs/ (should not be deployed)"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓${NC} No .env file in docs/"
fi

echo ""
echo "=== Checking Links ==="
echo ""

# Check for broken internal links (basic check)
if [ -f "docs/index.html" ]; then
    BROKEN_LINKS=0
    for file in docs/*.html; do
        if [ -f "$file" ]; then
            # Extract .html links and check if they exist
            links=$(grep -o 'href="[^"]*\.html"' "$file" 2>/dev/null | sed 's/href="//;s/"//' | grep -v "https://" || true)
            for link in $links; do
                if [ ! -f "docs/$link" ]; then
                    echo -e "${YELLOW}⚠${NC} Warning: Possibly broken link in $file: $link"
                    BROKEN_LINKS=$((BROKEN_LINKS + 1))
                fi
            done
        fi
    done
    if [ $BROKEN_LINKS -eq 0 ]; then
        echo -e "${GREEN}✓${NC} No broken internal links detected"
    else
        WARNINGS=$((WARNINGS + BROKEN_LINKS))
    fi
else
    echo -e "${YELLOW}⚠${NC} Could not check links (index.html not found)"
fi

echo ""
echo "=== Repository Configuration Checks ==="
echo ""

# Check if we're in a git repository
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Git repository detected"
    
    # Check current branch
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo "  Current branch: $BRANCH"
    
    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        echo -e "${YELLOW}⚠${NC} Warning: Uncommitted changes detected"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "${GREEN}✓${NC} No uncommitted changes"
    fi
else
    echo -e "${RED}✗${NC} Not in a git repository"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "================================================"
echo "Validation Summary"
echo "================================================"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Commit and push your changes to the main branch"
    echo "2. Go to GitHub Settings → Pages"
    echo "3. Set source to 'GitHub Actions'"
    echo "4. Wait for the workflow to complete"
    echo "5. Visit https://durangogt.github.io/genai-summarizer-web-app/"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Validation completed with $WARNINGS warning(s)${NC}"
    echo "Review the warnings above, but deployment should work."
    echo ""
    exit 0
else
    echo -e "${RED}✗ Validation failed with $ERRORS error(s) and $WARNINGS warning(s)${NC}"
    echo "Please fix the errors above before deploying."
    echo ""
    exit 1
fi
