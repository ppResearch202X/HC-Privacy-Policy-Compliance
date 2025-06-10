# HC-Privacy-Policy-Compliance

Health Connect (HC) is Google’s new Android platform layer that lets mobile‑health (mHealth) apps exchange sensitive health data while giving users fine‑grained control. To make that sharing transparent, every HC‑integrating app must provide a dedicated privacy‑rationale Activity explaining why permissions are needed and how data will be handled.

This repository contains the source code for the first large‑scale compliance audit of those requirements. We analysed 673 real‑world mHealth APKs using a pipeline that blends automated UI exploration, static code analysis, and machine‑learning classifiers. Our study shows that 50.4 % of apps either omit or incorrectly implement the mandated dialog, and that 76.2 % of privacy‑policy texts fail to justify the requested permissions.

Inside you’ll find:

Automated UI testing scripts that exercise each app to detect the mandated privacy‑rationale dialog at runtime.

Python sources for machine‑learning experiments, including training and evaluation code, plus LLM‑driven scripts for static component identification and privacy‑policy disclosure analysis.

Reproducible notebooks and result files that back every figure and table in the paper.

In all, these resources demonstrate how static code features can power automated privacy‑compliance auditing at scale and provide a benchmark for future research.
