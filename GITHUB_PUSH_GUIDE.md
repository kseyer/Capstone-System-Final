# How to Push Your Code to GitHub

GitHub's web interface has a 25MB file size limit. You need to use Git commands instead. Here's how:

## Step 1: Install Git (if not installed)

1. Download Git from: https://git-scm.com/download/win
2. Install it with default settings
3. **Restart your terminal/PowerShell** after installation

## Step 2: Verify Git Installation

Open PowerShell and run:
```powershell
git --version
```

If it shows a version number, Git is installed correctly.

## Step 3: Navigate to Your Project

```powershell
cd C:\Projects\beauty_clinic_django
```

## Step 4: Initialize Git Repository (if not already done)

```powershell
git init
```

## Step 5: Make Sure .gitignore is Working

The `.gitignore` file should already exclude large files. Verify it exists and contains:
- `venv/` (virtual environment)
- `db.sqlite3` (database)
- `media/` (uploaded files)
- `backups/` (backup files)
- `__pycache__/` (Python cache)
- `*.pyc` (compiled Python files)

## Step 6: Add Files to Git

**IMPORTANT**: Only add source code files, NOT large files:

```powershell
# Add all files (gitignore will automatically exclude large files)
git add .
```

If you want to see what will be added first:
```powershell
git status
```

This shows which files will be committed. Large files like `venv/`, `db.sqlite3`, and `media/` should NOT appear.

## Step 7: Commit Your Changes

```powershell
git commit -m "Initial commit - Beauty Clinic Django app ready for Render deployment"
```

## Step 8: Create Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `beauty-clinic-django` (or your preferred name)
3. **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click "Create repository"

## Step 9: Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

```powershell
# Replace YOUR_USERNAME and REPO_NAME with your actual values
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

**Example:**
```powershell
git remote add origin https://github.com/johndoe/beauty-clinic-django.git
git branch -M main
git push -u origin main
```

## Step 10: Enter GitHub Credentials

When you push, you'll be asked for:
- **Username**: Your GitHub username
- **Password**: Use a **Personal Access Token** (not your GitHub password)

### How to Create Personal Access Token:

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name: "Beauty Clinic Project"
4. Select scopes: Check `repo` (full control of private repositories)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)
7. Use this token as your password when pushing

## Troubleshooting

### Error: "File too large"
If you still get this error, a large file might be tracked. Remove it:

```powershell
# Remove large files from git tracking (but keep them locally)
git rm --cached db.sqlite3
git rm --cached -r venv/
git rm --cached -r media/
git rm --cached -r backups/

# Commit the removal
git commit -m "Remove large files from tracking"
git push
```

### Error: "Authentication failed"
- Make sure you're using a Personal Access Token, not your password
- Check that the token has `repo` permissions

### Error: "Remote origin already exists"
If you already added a remote:
```powershell
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
```

### Files Still Too Large?
Check file sizes:
```powershell
# Find large files (Windows PowerShell)
Get-ChildItem -Recurse | Where-Object {$_.Length -gt 10MB} | Select-Object FullName, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB,2)}}
```

Make sure all large files are in `.gitignore`!

## Quick Reference - Complete Commands

```powershell
# Navigate to project
cd C:\Projects\beauty_clinic_django

# Initialize (if needed)
git init

# Check what will be added
git status

# Add files
git add .

# Commit
git commit -m "Initial commit"

# Connect to GitHub (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## After Pushing Successfully

Once your code is on GitHub, you can:
1. Go to Render.com
2. Connect your GitHub repository
3. Deploy your app!

See `RENDER_DEPLOYMENT.md` for deployment instructions.

