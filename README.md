<div align="center">

# 🏥 MediTrack: AI-Powered Medication Adherence Platform

<img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=32&duration=2800&pause=2000&color=00D9FF&center=true&vCenter=true&width=940&lines=Predict+%7C+Analyze+%7C+Optimize;Medication+Adherence+Intelligence" alt="Typing SVG" />

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%" />

</div>

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [✨ Key Features](#-key-features)
- [🚀 Tech Stack](#-tech-stack)
- [🏗️ Architecture](#️-architecture)
- [⚡ Quick Start](#-quick-start)
- [🎨 Screenshots](#-screenshots)
- [🧠 ML Model](#-ml-model)
- [📊 Analytics](#-analytics)
- [🤝 Contributing](#-contributing)

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%" />

## 🎯 Overview

<div align="center">

</div>

**MediTrack** is an AI-powered healthcare platform that predicts medication adherence patterns and provides actionable insights to improve patient outcomes. By analyzing multiple factors including age, medication complexity, side effects, and socioeconomic conditions, the system delivers **85-90% accurate** adherence predictions.

### 💡 The Problem
- **50%** of patients don't take medications as prescribed
- Non-adherence costs the US healthcare system **$290 billion annually**
- Leads to **125,000 deaths** per year in the US alone

### ✅ The Solution
Real-time AI predictions + Smart analytics + Personalized recommendations = Better patient outcomes

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%" />

## ✨ Key Features

<table>
<tr>
<td width="50%">

### 🧠 AI Prediction Engine
- Multi-factor analysis (9 parameters)
- Gradient Boosting algorithm
- Real-time risk scoring (0-100)
- Confidence intervals

</td>
<td width="50%">

### 📸 OCR Prescription Scanner
- Upload prescription images
- Automatic text extraction
- Medicine name detection
- One-click form population

</td>
</tr>
<tr>
<td width="50%">

### 💊 Drug Interaction Checker
- Real-time interaction detection
- Severity classification
- Clinical recommendations
- 13,000+ medicine database

</td>
<td width="50%">

### 📊 Advanced Analytics
- Patient cohort analysis
- Trend visualization
- Risk distribution charts
- Exportable reports

</td>
</tr>
<tr>
<td width="50%">

### 🎯 Smart Recommendations
- Context-aware advice
- Priority-based interventions
- Evidence-based strategies
- Personalized action plans

</td>
<td width="50%">

### 👥 Patient Management
- Complete patient profiles
- Historical tracking
- Search & filter capabilities
- Bulk data import/export

</td>
</tr>
</table>

<div align="center">
<img src="https://media.giphy.com/media/L8K62iTDkzGX6/giphy.gif" width="400"/>
</div>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%" />

## 🚀 Tech Stack

<div align="center">

### Backend
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)

### Frontend
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?style=flat-square&logo=chart.js&logoColor=white)

### AI/ML & Tools
![Tesseract](https://img.shields.io/badge/Tesseract_OCR-3D3D3D?style=flat-square)
![Gradient Boosting](https://img.shields.io/badge/Gradient_Boosting-FF6F00?style=flat-square)
![JSON](https://img.shields.io/badge/JSON-000000?style=flat-square&logo=json&logoColor=white)

</div>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%" />

## 🏗️ Architecture

<div align="center">
<img src="https://media.giphy.com/media/xT9IgzoKnwFNmISR8I/giphy.gif" width="350"/>
</div>

```mermaid
graph TB
    A[User Interface] --> B[Flask Backend]
    B --> C[ML Predictor]
    B --> D[OCR Processor]
    B --> E[Drug Checker]
    C --> F[(Training Data)]
    D --> G[Tesseract OCR]
    E --> H[(Medicine DB)]
    B --> I[Analytics Engine]
    I --> J[Chart.js Visualization]
```

### 📁 Project Structure
```
📦 AIML_HACKATHON
├── 📄 app.py                      # Flask application entry point
├── 📂 model/
│   ├── predictor.py               # ML prediction engine
│   └── __init__.py
├── 📂 utils/
│   ├── ocr_processor.py           # Prescription OCR
│   ├── drug_interaction_checker.py # Drug interactions
│   ├── medicine_db.py             # Medicine database
│   └── prescription_reader.py
├── 📂 static/
│   ├── css/style.css
│   └── js/
│       ├── predict_enhanced.js    # Prediction UI logic
│       ├── analytics.js           # Analytics dashboard
│       └── patients.js            # Patient management
├── 📂 data/
│   ├── training_data.csv          # ML training dataset
│   └── patients.json              # Patient records
└── 📂 use_dataset/
    ├── medicine_dataset.csv       # 13,000+ medicines
    └── db_drug_interactions.csv   # Drug interactions DB
```

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%" />

## ⚡ Quick Start

<div align="center">
<img src="https://media.giphy.com/media/ZVik7pBtu9dNS/giphy.gif" width="350"/>
</div>

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Tesseract OCR (optional, for prescription scanning)

### Installation

```bash
# Clone the repository
git clone https://github.com/Dharaneesh20/AIML_HACKATHON_SECE.git
cd AIML_HACKATHON_SECE

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install flask numpy pandas scikit-learn werkzeug pytesseract pillow

# Run the application
python app.py
```

### 🌐 Access the Platform
Open your browser and navigate to:
```
http://localhost:5000
```

### 🎯 Quick Demo
1. **Predict Adherence**: Navigate to Predict tab → Enter patient details → Get AI prediction
2. **Upload Prescription**: Use OCR feature → Upload image → Auto-extract medicines
3. **View Analytics**: Check Analytics tab → Explore patient trends and insights
4. **Manage Patients**: Go to Patients tab → View/Search saved patient records

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%" />

## 🎨 Screenshots

<div align="center">

### 🏠 Dashboard Overview
![Dashboard](https://via.placeholder.com/800x400/0d1117/00d9ff?text=Interactive+Dashboard+with+Real-time+Analytics)

### 🔮 AI Prediction Interface
![Prediction](https://via.placeholder.com/800x400/0d1117/4caf50?text=Multi-factor+AI+Prediction+Engine)

### 📊 Analytics Dashboard
![Analytics](https://via.placeholder.com/800x400/0d1117/ff9800?text=Advanced+Data+Visualization+%26+Insights)

</div>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%" />

## 🧠 ML Model

<div align="center">
<img src="https://media.giphy.com/media/LaVp0AyqR5bGsC5Cbm/giphy.gif" width="350"/>
</div>

### Algorithm: Gradient Boosting Regressor

**Why Gradient Boosting?**
- ✅ Handles non-linear relationships
- ✅ Robust to outliers
- ✅ High accuracy (85-90%)
- ✅ Feature importance analysis

### Input Features (9 Parameters)

| Feature | Type | Impact |
|---------|------|--------|
| Age | Numeric | Elderly patients show different patterns |
| Number of Medications | Numeric | Polypharmacy burden |
| Dosage Frequency | Numeric | Complexity factor |
| Missed Doses | Numeric | Historical behavior |
| Side Effects | Binary | Negative experience |
| Comorbidities | Numeric | Health complexity |
| Cost Concern | Binary | Economic barrier |
| Reminder System | Binary | +20-30% adherence |
| Support System | Binary | Social support impact |

### Output

```json
{
  "adherence_score": 72.5,
  "risk_level": "Medium",
  "confidence": "High",
  "recommendations": [
    "Enable medication reminders",
    "Schedule follow-up consultation"
  ]
}
```

### Model Performance
- **Accuracy**: 85-90%
- **Training Samples**: 1000+
- **Cross-validation**: 5-fold
- **Mean Absolute Error**: <8 points

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%" />

## 📊 Analytics

<div align="center">
<img src="https://media.giphy.com/media/3o7btPCcdNniyf0ArS/giphy.gif" width="350"/>
</div>

### Key Insights

📈 **Adherence Trends**
- Track adherence scores over time
- Identify seasonal patterns
- Monitor intervention effectiveness

👥 **Patient Cohorts**
- Age group analysis
- Medication complexity correlation
- Risk distribution visualization

💊 **Medication Impact**
- Polypharmacy burden assessment
- Drug interaction frequency
- Reminder system effectiveness: **+25% adherence**

🎯 **Actionable Intelligence**
- High-risk patient identification
- Intervention prioritization
- Predictive alerts

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%" />

## 🔮 Future Enhancements

<div align="center">
<img src="https://media.giphy.com/media/l0HlMSVVw9zqmClLq/giphy.gif" width="350"/>
</div>

- 🔔 **Real-time Notifications**: SMS/Email alerts for missed doses
- 📱 **Mobile App**: iOS & Android companion apps
- 🌐 **Multi-language Support**: Accessibility for global users
- 🤖 **Deep Learning**: LSTM networks for time-series prediction
- 🔗 **EHR Integration**: Connect with hospital systems
- 📊 **Advanced Analytics**: Predictive modeling for hospital readmissions
- 🔐 **HIPAA Compliance**: Enhanced security features
- 🧬 **Genomic Data**: Personalized medicine based on genetics

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%" />

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. 🍴 Fork the repository
2. 🔨 Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push to the branch (`git push origin feature/AmazingFeature`)
5. 🎉 Open a Pull Request

<div align="center">
<img src="https://media.giphy.com/media/du3J3cXyzhj75IOgvA/giphy.gif" width="300"/>
</div>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%" />

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%" />

## 👥 Team

<div align="center">

**AIML Hackathon - SECE**

Built with ❤️ by Team SECE

[![GitHub](https://img.shields.io/badge/GitHub-Dharaneesh20-181717?style=for-the-badge&logo=github)](https://github.com/Dharaneesh20)

</div>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%" />

<div align="center">

### 🌟 If you find this project useful, please consider giving it a star!

<img src="https://media.giphy.com/media/3o7abB06u9bNzA8lu8/giphy.gif" width="200"/>

**Made with 💊 for better healthcare outcomes**

</div>

---

<div align="center">

© 2025 MediTrack | AI-Powered Healthcare Innovation

</div>
