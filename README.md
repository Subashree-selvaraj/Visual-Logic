# ⚡ VisualFlow – AI Code Flow Visualizer

> **Understanding the logic isn’t optional. It’s the foundation.**

VisualFlow is an AI-powered code understanding tool that helps developers and students **see how their code works**, not just read it.

Instead of jumping straight into syntax and guessing how things connect, VisualFlow allows you to **visualize the step-by-step execution of code** using interactive flowcharts and clear, human-friendly explanations.

---

## 🧠 Why VisualFlow?

When learning or writing code, one question matters most:

> **“Do I really understand what’s happening here?”**

Many developers:
- Memorize syntax
- Copy examples
- Hope clarity comes later

VisualFlow was built for those who believe **clarity should come before coding**.

It bridges the gap between:
- Knowing **how code looks**
- Understanding **how code works**

---

## 🚀 What VisualFlow Does

- Paste your code
- Instantly generates a **clear, structured flowchart**
- Explains the logic in **plain, human-friendly language**
- Highlights conditions, loops, function calls, and returns
- Makes complex logic easy to reason about

---

## ✨ Features

- 📌 AI-powered code analysis  
- 🔁 Step-by-step logical breakdown  
- 🧩 Interactive flowchart generation (Graphviz)  
- 📖 Simple, student-friendly explanations  
- 🎯 Focused on logic, not just syntax  
- 🧠 Ideal for DSA, problem-solving, and learning new concepts  

---

## 🛠 Tech Stack

### Frontend & UI
- Streamlit  

### AI & APIs
- OpenRouter API  
- OpenAI-compatible SDK  

### Visualization
- Graphviz  

### Backend / Core
- Python  
- dotenv  

---

## 🧱 How It Works (High-Level)

1. User pastes code into the input area
2. Code is analyzed by an AI model
3. AI returns:
   - Structured JSON representing logic flow
   - A human-readable explanation
4. JSON is converted into a **Graphviz flowchart**
5. Explanation is displayed alongside the visual flow

---

## 🎥 Live Demo

🔗 **Live Application**  
https://visual-logic.streamlit.app/

## 📦 Installation & Setup (Local)

### 1️⃣ Clone the repository
```bash
git clone https://github.com/Subashree-selvaraj/Visual-Logic.git
cd Visual-Logic

2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Setup environment variables

Create a .env file:

OPENROUTER_API_KEY=your_openrouter_api_key

4️⃣ Run the app
streamlit run app.py
