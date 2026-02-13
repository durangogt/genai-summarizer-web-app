# GitHub Pages Deployment Guide

This document provides instructions for deploying the GenAI Summarizer Web App documentation to GitHub Pages.

## 📋 Overview

This repository includes a static documentation site in the `docs/` directory that is automatically deployed to GitHub Pages using GitHub Actions. The documentation provides:

- Project overview and features
- Setup and installation guide
- Complete API reference
- Usage examples and best practices

## 🔐 Security Considerations

This deployment follows security best practices for public repositories:

### ✅ What's Safe to Deploy
- **Static HTML/CSS documentation** - No executable code on GitHub Pages
- **Public API documentation** - Describes endpoints but contains no secrets
- **Setup guides** - Installation instructions without credentials
- **Example code** - Sample requests with placeholder values

### ❌ What's NOT Included
- **No API keys or secrets** - All credentials stay in environment variables
- **No backend code** - The Python application is not deployed to Pages
- **No database connections** - Documentation is static HTML only
- **No user data** - No sensitive information exposed

### 🛡️ Workflow Security Features
- **Minimal permissions**: Uses least-privilege GITHUB_TOKEN permissions
- **Shallow clones**: `fetch-depth: 1` reduces attack surface
- **Concurrency control**: Prevents race conditions in deployments
- **Environment protection**: Leverages GitHub's environment security
- **Latest actions**: Uses up-to-date, maintained GitHub Actions

## 🚀 Setup Instructions

### Step 1: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages** (in the left sidebar)
3. Under **Source**, select **GitHub Actions**
4. Click **Save**

> **Note**: You do NOT need to select a branch. The GitHub Actions workflow will handle deployment.

### Step 2: Verify Workflow

1. Go to **Actions** tab in your repository
2. You should see the "Deploy to GitHub Pages" workflow
3. If on `main` branch, the workflow will run automatically on your next push
4. You can also manually trigger it using the "Run workflow" button

### Step 3: Access Your Site

Once deployed, your documentation will be available at:

```
https://durangogt.github.io/genai-summarizer-web-app/
```

The URL format is: `https://<username>.github.io/<repository-name>/`

## 📝 How It Works

### Workflow Trigger
The deployment workflow (`.github/workflows/deploy-pages.yml`) is triggered by:
- **Automatic**: Any push to the `main` branch
- **Manual**: Using the "Run workflow" button in GitHub Actions

### Deployment Process
1. **Checkout**: Code is checked out from the repository
2. **Setup**: GitHub Pages environment is configured
3. **Upload**: The `docs/` directory is packaged as an artifact
4. **Deploy**: Artifact is deployed to GitHub Pages environment

### Deployment Time
- Initial deployment: ~2-3 minutes
- Subsequent updates: ~1-2 minutes

## 🔧 Troubleshooting

### Issue: "Pages build and deployment" failing

**Solution**: Ensure GitHub Pages is set to use "GitHub Actions" as the source:
1. Go to Settings → Pages
2. Under "Source", select "GitHub Actions"
3. Do NOT select "Deploy from a branch"

### Issue: 404 errors on deployed site

**Solution**: Check that:
1. The `docs/` directory exists and contains `index.html`
2. The workflow ran successfully (check Actions tab)
3. Wait a few minutes for DNS propagation

### Issue: Workflow permission denied

**Solution**: Enable workflow permissions:
1. Go to Settings → Actions → General
2. Scroll to "Workflow permissions"
3. Select "Read and write permissions"
4. Check "Allow GitHub Actions to create and approve pull requests"
5. Click Save

### Issue: Custom domain not working

**Solution**: 
1. Add a `CNAME` file to `docs/` directory with your domain
2. Configure DNS settings with your domain provider
3. Go to Settings → Pages and add your custom domain

## 🎨 Customizing the Documentation

### Adding New Pages
1. Create a new HTML file in `docs/` directory
2. Use the existing pages as templates
3. Link to `styles.css` for consistent styling
4. Add navigation links in the header

### Updating Styles
- Edit `docs/styles.css` to modify the visual theme
- Changes will be deployed automatically on push to `main`

### Testing Locally
Preview your changes before deploying:

```bash
# Navigate to docs directory
cd docs

# Start a local web server
python -m http.server 8080

# Open http://localhost:8080 in your browser
```

## 📊 Monitoring Deployments

### View Deployment Status
1. Go to **Actions** tab
2. Click on the latest workflow run
3. View logs for each step (build, deploy)

### View Live Site Status
1. Go to **Settings** → **Pages**
2. See the current deployment status and URL
3. View deployment history

### Environment Details
- **Environment**: github-pages
- **Branch**: Deployments are from workflow artifacts, not branches
- **URL**: Auto-generated based on repository name

## 🔄 Updating the Documentation

### Regular Updates
1. Edit files in `docs/` directory
2. Commit changes: `git commit -m "Update documentation"`
3. Push to main: `git push origin main`
4. Workflow runs automatically
5. Changes live in 1-2 minutes

### Emergency Rollback
If you need to rollback a deployment:
1. Go to **Actions** tab
2. Find a previous successful workflow run
3. Click "Re-run all jobs"
4. Or revert your commit and push

## 📚 Additional Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Actions Permissions](https://docs.github.com/en/actions/security-guides/automatic-token-authentication)
- [Custom Domains](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)

## ✅ Checklist

Before deploying to production:

- [ ] Repository Settings → Pages is set to "GitHub Actions"
- [ ] Workflow file exists at `.github/workflows/deploy-pages.yml`
- [ ] Documentation files exist in `docs/` directory
- [ ] No secrets or API keys in documentation files
- [ ] Navigation links work correctly
- [ ] Styles are applied properly
- [ ] All images and assets load correctly
- [ ] Responsive design works on mobile devices
- [ ] Accessibility features are functional

## 🆘 Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#-troubleshooting) section above
2. Review workflow logs in the Actions tab
3. Consult [GitHub Pages documentation](https://docs.github.com/en/pages)
4. Open an issue in the repository

## 📄 License

This documentation deployment configuration is part of the GenAI Summarizer Web App project and follows the same license.
