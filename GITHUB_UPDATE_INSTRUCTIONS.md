# GitHub Update Instructions

These commands assume the repository name is:

`engineering-portfolio`

and that you are inside:

`/Users/hoodieb/Documents/VSCODE/Portfolio`

## First-time publish to GitHub

If the GitHub repo does not exist yet, create an empty public repository on GitHub named:

`engineering-portfolio`

Then run:

```bash
cd /Users/hoodieb/Documents/VSCODE/Portfolio
git remote set-url origin git@github.com:BYasuoka/engineering-portfolio.git
git push -u origin main
```

Make sure your GitHub SSH key is already added to your GitHub account.

## Normal update workflow

After you make changes to the portfolio:

```bash
cd /Users/hoodieb/Documents/VSCODE/Portfolio
git status
git add .
git commit -m "Update portfolio site"
git push
```

## Check the current remote

If you ever want to verify the repo is using SSH:

```bash
cd /Users/hoodieb/Documents/VSCODE/Portfolio
git remote -v
```

You should see:

```bash
origin  git@github.com:BYasuoka/engineering-portfolio.git (fetch)
origin  git@github.com:BYasuoka/engineering-portfolio.git (push)
```

## Run the site locally before pushing

Use the Python server so the budget form works:

```bash
cd /Users/hoodieb/Documents/VSCODE/Portfolio
python3 server.py
```

Then open:

`http://127.0.0.1:8000`

## Optional: more descriptive commit messages

Examples:

```bash
git commit -m "Add new project images"
git commit -m "Update resume and homepage copy"
git commit -m "Improve budget calculator form"
```
