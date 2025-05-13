# 🔍 SEO Auditor Tool

**SEO Auditor** is a powerful tool for analyzing websites and identifying key SEO metrics and issues. Designed for developers, digital marketers, and SEO professionals, this tool provides both **basic** and **Intermediate** SEO audits using a modern Python-based tech stack framework **Streamlit**.

---

## 🚀 Features

### ✅ Basic SEO Checks
- Title tag and meta description analysis
- Header tags analysis (H1–H6)
- Image <`alt`> tag validation
- Keyword density calculation
- Readability score

### 🧠 Advanced SEO Checks
- Backlink analysis
- Toxic link detection
- Keyword ranking
- AI-based recommendations
- Report generation in the form of .MD , Excel-Report

### 🛠️ Technical SEO Audit
- Canonical & duplicate content analysis
- Mobile-friendliness check
- HTTPS and SSL security audit

---

## 🧰 Tech Stack

- **Frontend**: Streamlit (Python)
- **Backend**: Django + FastAPI
- **Database**: Supabase
- **APIs Used**:
  - Google Search Console API
  - PageSpeed Insights API
  - OpenAI API

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/Rpal-29/Seo-Audit.git
cd Seo-Audit

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt


# Run the Streamlit frontend
streamlit run Dashboard.py

# Make sure backend (Django & FastAPI) servers are running
# Use Swagger or Postman to test API endpoints


Contributions are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request
