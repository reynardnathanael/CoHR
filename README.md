# CoHR
LLM as a decision-support or second-review assistant for resume screening

## 1. Introduction
HR (human resources) professionals handle numerous daily tasks and act as gatekeepers in recruitment, deciding which candidates advance to the next stage. However, this process presents challenges: reviewing full resumes is time-consuming, and HR often manages diverse roles they may not fully understand, making accurate evaluation difficult. For instance, an HR professional may lack familiarity with the required skills for a Field Application Engineer but still must decide whether to invite the candidate for a phone interview. Therefore, our objective is to use LLMs to support more efficient and effective resume screening decisions.

## 2. Dataset Information

## 3. Environment Setup
### File Structure
```

```

## 4. Model Framework
### 4.1. Outline of the architecture
![Model Framework](img/model_framework.png)

## 5. Results

## 6. Demo Video

## 7. Installation

### Front-end (Vue.js + Vite + Tailwind CSS + PrimeVue)
First, navigate to the front-end directory and install the required npm packages:
```bash
cd front-end
npm install
npm update
```

### Back-end (FastAPI)
Navigate to the back-end directory. We recommend creating a virtual environment (e.g., using `conda` or `venv`) before installing the Python dependencies:
```bash
cd back-end
# Create and activate your virtual environment here (e.g., conda create -n cohr python=3.13 -y && conda activate cohr)
pip install -r requirements.txt
```

## 8. Execution

To run the application, you will need to start both the front-end and back-end servers in separate terminal instances.

### Front-end Server
```bash
cd front-end
npm run dev
```

### Back-end Server
```bash
cd back-end
uvicorn main:app --reload --port 8080
```

## Reference