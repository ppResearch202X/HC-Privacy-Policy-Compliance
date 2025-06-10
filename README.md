# HC Privacy Policy Compliance

Health Connect (HC) is Google’s new Android platform layer that lets mobile‑health (mHealth) apps exchange sensitive health data while giving users fine‑grained control. To make that sharing transparent, every HC‑integrating app must provide a dedicated *privacy‑rationale* Activity explaining why permissions are needed and how data will be handled.

This repository contains the artifacts, code, and datasets for the **first large‑scale compliance audit** of those requirements. We analysed **673 real‑world mHealth APKs** using a pipeline that blends automated UI exploration, static code analysis, and machine‑learning classifiers. Our study shows that **50.4 % of apps either omit or incorrectly implement the mandated dialog**, and that **76.2 % of privacy‑policy texts fail to justify the requested permissions**.

---

## Table of Contents

* [How to Use](#how-to-use)

  * [Setup](#setup)
  * [Usage](#usage)
  

---

## How to Use

### Setup

Install the required libraries:

```bash
pip install -r requirements.txt
```

### Usage

RQ1 – Automated UI‑testing pipeline

`RQ1/UI_testing.sh` is a Bash script meant to be run **inside the Android Studio terminal (or any shell where `adb` is on the PATH)**. It installs each APK, exercises the UI, and captures screenshots of the Health Connect permission rationale dialog.
* **Running the script**

  ```bash
  cd RQ1
  chmod +x UI_testing.sh        # first‑time only
  ./UI_testing.sh               # runs against every APK in $packageDir
  ```


  
---


### Contributing

If you’d like to contribute, please open an issue or pull request.

### License

This project is licensed under the Apache 2.0 License – see the `LICENSE` file for details.
