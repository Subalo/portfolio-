# Subalo Belay — Electrical Engineer

A static, English portfolio for an Electrical and Electronics Engineering graduate from Ariel University, specializing in Computers and Communications.

## Projects

- **Smart Lock System:** PYNQ-Z2, FPGA/VHDL, Vivado, Python, OpenCV, sensors, stepper control and Telegram notifications. B.Sc. final project grade: 93/100.
- **Digital Safe:** the existing logic-based safe project, including its Arduino implementation and all three original attachments.

## Local review

Open index.html in a browser, or serve this directory with any static HTTP server. No installation or build is required.

Validate files, internal links, image attributes and the preservation of the original attachments:

    python3 scripts/check-site.py
    node --check site.js

Create a single-file preview with embedded styles, scripts and images:

    python3 scripts/make-preview.py

The generated review/portfolio-preview.html can be opened directly. Its document links point to the review branch on GitHub. The generated preview is not a production file.

## GitHub Pages

Publish from the main branch, repository root. Relative asset URLs support the /portfolio-/ project path. The .nojekyll file prevents Jekyll processing. Merge the review branch only after owner approval.

Before the redesign, the original site was preserved on:

    backup/pre-redesign-2026-10-15

The duplicate site's files were backed up on the same branch name in Subalo/subalo.github.io before its homepage and stylesheet were removed. Its project attachments were preserved.

## Content and media

See docs/content-sources.md for the source of the project facts and images. The new Smart Lock report and poster are publication copies with the personal identifier, Telegram token and chat identifier removed. The originals were not modified. No tracking, analytics or contact-form backend is used.
