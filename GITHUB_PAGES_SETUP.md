# GitHub Pages Deployment Instructions

## Objective
Enable GitHub Pages for the VoiceBridge AI repository so judges can access the interactive demo at:
**https://yuga-i2.github.io/VoiceBridge_AI**

## Steps to Enable (Web Interface)

### 1. Navigate to Repository Settings
- Go to: https://github.com/yuga-i2/VoiceBridge_AI
- Click the "Settings" tab (gear icon in top navigation)

### 2. Access Pages Settings
- In the left sidebar, scroll down and click "Pages" (under "Code and automation" section)

### 3. Configure Source
- Under "Source" section:
  - Select: **Deploy from a branch**
  - Branch: **master**
  - Folder: **/ (root)**

### 4. Save Configuration
- Click the "Save" button
- Wait 1-2 minutes for GitHub to build and deploy

### 5. Verify Deployment
- GitHub Pages will show a notification: "Your site is published at: https://yuga-i2.github.io/VoiceBridge_AI/"
- Click the link to verify the interactive demo loads correctly

## What Gets Deployed
- `index.html` from the repository root
- The interactive Sahaya demo with:
  - Hero section with key stats (135M farmers, ₹15 cost, 180× savings)
  - Problems cards (70% farmers excluded, ₹2,700 traditional cost)
  - Interactive call simulator
  - AWS architecture cards
  - Economics comparison
  - Complete styling and animations

## Troubleshooting

### If pages doesn't appear after 3 minutes:
1. Check that `index.html` is in the repository root
2. Go back to Settings → Pages
3. Verify the source is set to "master" branch, "/" folder
4. Clear browser cache and try again

### If styling looks broken:
- This shouldn't happen as all CSS is embedded in the HTML file
- If it does, try a hard refresh (Ctrl+Shift+R or Cmd+Shift+R)

### If interactive features don't work:
- All functionality is vanilla JavaScript (no external libraries)
- Check browser console (F12) for any errors
- Try a different browser

## After Deployment

Update submission documents with the live demo link:
- README.md → Update demo video link
- Hackathon submission form → Include: https://yuga-i2.github.io/VoiceBridge_AI

## Timeline
- Deployment is usually instant (1-2 minutes)
- Once published, the site will be live for judges to access
- Updates to `index.html` will auto-deploy within minutes

---

**Status:** Ready for GitHub Pages enablement. All files committed and in place.
