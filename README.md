# 📊 Production Analyser

[![Python Version](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/yourusername/production-analyser?style=social)](https://github.com/yourusername/production-analyser)

---

## 🧠 Overview

**Production Analyser** is a Python-based industrial dashboard designed to decode the rhythm of your production line. It captures real-time metrics from PLC systems, visualizes fault and delay patterns through dynamic pie charts, and empowers engineers with actionable insights—all within a modular, customizable interface.

Whether you're simulating data with a mock PLC server or deploying in a live factory environment, the tool adapts to your workflow with configurable tags, intuitive layouts, and a clean separation of logic. Built with PyQt5 and backed by pandas and NumPy, it’s engineered for responsiveness, clarity, and rapid iteration.

> _From hackathon heroes to factory floor pros—empower your team to monitor, analyze, and refine production performance like never before._

---

  ![Description of image](https://drive.google.com/uc?export=view&id=FILE_ID)
  <p><em>Real-time fault analysis dashboard—your production line, visualized.</em></p>


---

## 🚀 Features

- **🔌 Real-Time PLC Integration** – Pull metrics directly from PLC systems or simulate with a built-in mock server.
- **📊 Dynamic Visualizations** – Interactive pie charts for fault/delay patterns, plus customizable graphs.
- **🧩 Modular & Customizable** – Configure tags via JSON/Excel, rearrange layouts, and extend with plugins.
- **📈 Actionable Insights** – Automated alerts, trend analysis, and exportable reports.
- **⚡ Responsive Performance** – Powered by PyQt5 for smooth GUI, with pandas and NumPy for fast data crunching.
- **🌍 Cross-Environment Ready** – Works in simulated dev setups or rugged industrial deployments.

---

## 🛠 Tech Stack

| Category         | Technologies                     |
|------------------|----------------------------------|
| Language         | Python 3.x                       |
| GUI Framework    | PyQt5                            |
| Data Handling    | pandas, NumPy                    |
| Configuration    | JSON, Excel (via openpyxl)       |
| Visualization    | Matplotlib (integrated with PyQt5) |
| Async Polling    | asyncio                          |

---

## 📦 Installation

Getting started is easy! Follow these steps:

```bash
# Clone the repository
git clone https://github.com/yourusername/production-analyser.git
cd production-analyser

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```
🌟 Acknowledgements
Built with love using open-source magic: PyQt5, pandas, and NumPy. Inspired by industrial IoT challenges at hackathons and real-world deployments. Thanks to the Python community for tools that make automation accessible.
