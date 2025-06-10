# HC Privacy Policy Compliance

Health Connect (HC) is Google’s new Android platform layer that lets mobile‑health (mHealth) apps exchange sensitive health data while giving users fine‑grained control. To make that sharing transparent, every HC‑integrating app must provide a dedicated *privacy‑rationale* Activity explaining why permissions are needed and how data will be handled.

This repository contains the artifacts, code, and datasets for the **first large‑scale compliance audit** of those requirements. We analysed **673 real‑world mHealth APKs** using a pipeline that blends automated UI exploration, static code analysis, and machine‑learning classifiers. Our study shows that **50.4 % of apps either omit or incorrectly implement the mandated dialog**, and that **76.2 % of privacy‑policy texts fail to justify the requested permissions**.

## Table of Contents

* [How to Use](#how-to-use)

  * [Setup](#setup)
  * [Usage](#usage)
  

## How to Use

### Setup

Install the required libraries:

```bash
pip install -r requirements.txt
```

### Usage

#### 1. RQ1 – Automated UI‑testing pipeline

`RQ1/UI_testing.sh` is a Bash script meant to be run **inside the Android Studio terminal (or any shell where `adb` is on the PATH)**. It installs each APK, exercises the UI, and captures screenshots of the Health Connect permission rationale dialog.

Running the script

  ```bash
  cd RQ1
  chmod +x UI_testing.sh        # first‑time only
  ./UI_testing.sh               # runs against every APK in $packageDir
  ```


#### 2. RQ2 - ML/LLM-based Accessibility Detection

`RQ2/` contains two approaches for identifying whether an app correctly implements the required *privacy‑rationale* Activity at code level.

| sub‑folder                 | purpose                                                                                                                                                                      |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`ML_based_detection/`**  | Traditional machine‑learning classifiers (`lr.py`, `rf.py`, `svm.py`) trained on static‑code embeddings (already extracted and shipped as `HC‑compatible_apps_embed_*.pkl`). |
| **`LLM_based_detection/`** | A lightweight script (`llm.py`) that queries a large‑language model to reason over raw Java source and rationale declaration text.                                                  |


* ML‑based detection

Running an experiment

  ```bash
  cd RQ2/ML_based_detection
  # pick any model script and run it
  python lr.py   # logistic regression
  python rf.py   # random forest
  python svm.py  # SVM with RBF kernel
  ```
  
  Each script automatically loads the pre‑computed embeddings, fits the model, prints accuracy / F1 / AUC to stdout, and writes predictions to `pred_<model>.csv`.

* LLM‑based detection

`RQ2/LLM_based_detection/llm.py` reads **rationale Java source files** and **privacy‑rationale declarations**. These input archives are hosted on our [project website](https://sites.google.com/view/privacyinmhealth/datasets) — download them and point the script to the extracted folders:

Running an experiment
```bash
cd RQ2/LLM_based_detection
python llm.py
```

The script streams model thoughts to the console and saves a JSON containing per‑app verdicts. Feel free to tweak the prompt or use a different API endpoint.

#### 3. RQ3 - Permission‑clarity & privacy‑policy disclosure analysis

`RQ3_src/` provides a **worked example on four apps**—two whose privacy policies are available as plain text and two where the policy is only visible in a screenshot. This mirrors the two extraction strategies described in the paper (link/UI copy‑paste vs. screenshot OCR).

| sub‑folder        | contents                                                                                      |
| ----------------- | --------------------------------------------------------------------------------------------- |
| `permission_png/` | Screenshots of the HC permission‑rationale dialog (`pp_1.png`, `pp_2.png`) for each demo app. |
| `pp_txt/`         | Plain‑text privacy‑policies for two apps where a hyperlink was available.                     |
| `pp_png/`         | Screenshots of privacy‑policy pages when text could not be captured directly.                 |
| `llm_analysis.py` | Driver script that runs permission‑clarity and disclosure scoring using OCR + an LLM prompt.  |

Running the sample analysis

```bash
cd RQ3_src
python llm_analysis.py 
```

The script will

1. OCR any screenshots in `pp_png/`;
2. Align permission requests with the policy text;
3. Query the LLM to score clarity / justification quality;
4. Save per‑app metrics to the output JSON and print a short table.

Grab the complete HC‑compatible dataset from our [project website]([https://example.com](https://sites.google.com/view/privacyinmhealth/datasets) and run the experiment to produce the JSON replicates the disclosure‑analysis numbers reported in Section 5 of the paper.


### Contributing

If you’d like to contribute, please open an issue or pull request.

### License

This project is licensed under the Apache 2.0 License – see the `LICENSE` file for details.
