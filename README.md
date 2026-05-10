# Portfolio Website Starter

This folder now contains a simple static portfolio website starter for your personal engineering portfolio.

## Files

- `index.html`: homepage with hero section and featured projects
- `resume.html`: resume page and PDF link
- `projects.html`: main page for project portfolio browsing
- `projects/`: project detail pages
- `project-files/`: source material, code, posters, and images tied to project pages
- `styles.css`: all site styling
- `script.js`: mobile navigation behavior
- `assets/`: images, documents, and placeholder graphics

## Fastest way to preview

From the `Portfolio` folder:

```bash
python3 server.py
```

Then open `http://localhost:8000`.

Use `server.py` if you want the interactive Python budget form to work. A plain static server or
double-clicking `index.html` will render the pages, but the budget API will not be available.

## First edits to make

1. Replace the placeholder project images with your poster, CAD renders, and screenshots.
2. Update the text in `index.html`, `resume.html`, `projects.html`, and each file in `projects/`.
3. Add links for your GitHub and any other profiles you want visible.
4. Keep future photos in `assets/images/` and documents in `assets/docs/`.
5. Keep raw project folders and downloadable project artifacts in `project-files/`.

## Current placeholder setup

- Some project cards still use placeholder SVG graphics where the source folder did not include a dedicated preview image.
- The budgeting project now includes a Python-backed demo form served through `server.py`.
- The LabVIEW stress-strain page now includes a generated graph from `4130 Steel 20C#1.lvm`.
- Navigation is already wired for desktop and mobile.
- Your current headshot lives in `assets/images/`.
- Your current resume PDF lives in `assets/docs/`.
- Incoming project folders are organized under `project-files/` to keep the top-level portfolio clean.

## Good next upgrade ideas

- Add a contact section
- Add a resume download button
- Add more project pages
- Deploy with GitHub Pages, Netlify, or Vercel
