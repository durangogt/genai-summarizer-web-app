# GitHub Pages Documentation

This directory contains the static documentation site for the GenAI Summarizer Web App, deployed to GitHub Pages.

## 🌐 Live Site

The documentation is automatically deployed to: `https://durangogt.github.io/genai-summarizer-web-app/`

## 📁 Structure

```
docs/
├── index.html       # Home page with project overview
├── setup.html       # Setup and installation guide
├── api.html         # API reference documentation
├── styles.css       # Shared styles for all pages
└── README.md        # This file
```

## 🚀 Deployment

The site is automatically deployed to GitHub Pages via GitHub Actions workflow:

1. **Trigger**: Pushes to the `main` branch or manual workflow dispatch
2. **Build**: The `docs/` directory is packaged as a Pages artifact
3. **Deploy**: Artifact is deployed to GitHub Pages environment

## 🔒 Security Features

- **Minimal permissions**: Workflow uses least-privilege permissions
- **Read-only content checkout**: Uses `fetch-depth: 1` for shallow clones
- **No secrets exposed**: Static HTML/CSS only, no API keys or credentials
- **Concurrency control**: Prevents deployment conflicts
- **Environment protection**: Uses GitHub Pages environment

## 🛠️ Local Development

To preview the documentation locally:

```bash
# Using Python's built-in HTTP server
cd docs
python -m http.server 8080

# Or using any other static file server
# Access at http://localhost:8080
```

## 📝 Updating Documentation

1. Edit HTML files in the `docs/` directory
2. Commit and push changes to `main` branch
3. GitHub Actions will automatically deploy updates
4. Changes will be live in ~1-2 minutes

## 🎨 Customization

- Modify `styles.css` to change the visual theme
- Update content in HTML files as needed
- Add new pages by creating additional HTML files
- Remember to link new pages in the navigation menu

## 🔗 Links

- **Repository**: https://github.com/durangogt/genai-summarizer-web-app
- **GitHub Pages Settings**: https://github.com/durangogt/genai-summarizer-web-app/settings/pages
- **Workflow Runs**: https://github.com/durangogt/genai-summarizer-web-app/actions

## ⚙️ Repository Configuration

To enable GitHub Pages for this repository:

1. Go to **Settings** → **Pages**
2. Under "Source", select **GitHub Actions**
3. Save the configuration

The workflow will automatically deploy on the next push to `main`.
