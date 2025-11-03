# Intelligent Vision Analysis Platform

<div align="center">
  <img src="https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white" alt="Angular">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch">
  <img src="https://img.shields.io/badge/Meta_SAM2-0468D7?style=for-the-badge&logo=meta&logoColor=white" alt="Meta SAM2">
  <img src="https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google Gemini">
  <img src="https://img.shields.io/badge/Milvus-00D1B2?style=for-the-badge&logo=vector-database&logoColor=white" alt="Milvus">
</div>

IVision is an advanced computer vision platform that combines cutting-edge AI models including Meta's Segment Anything Model 2 (SAM2), Google's Gemini/Gemma, and Grounding DINO for powerful image understanding. The platform features a modern Angular frontend and a FastAPI backend, with Milvus vector database enabling efficient similarity search and retrieval of visual content.

## 🌟 Features

- **Advanced Segmentation**: Leveraging Meta's SAM2 for precise object segmentation
- **Zero-shot Object Detection**: Powered by Grounding DINO for detecting objects without fine-tuning
- **Multimodal Understanding**: Google's Gemini/Gemma for rich image understanding and description
- **Vector Similarity Search**: Milvus database for efficient similarity search across image embeddings
- **Modern UI**: Clean and responsive interface built with Angular Material
- **Scalable Backend**: FastAPI-powered RESTful API with async support

<img width="969" height="462" alt="image" src="https://github.com/user-attachments/assets/3d3b11f9-1615-4487-9ede-e9225082ea96" />

<img width="973" height="468" alt="image" src="https://github.com/user-attachments/assets/db4c6245-bd57-4b68-af34-921bf5a0f8df" />

<img width="967" height="460" alt="image" src="https://github.com/user-attachments/assets/f7192abd-f19b-4eb9-825a-38834435facc" />

<img width="966" height="466" alt="image" src="https://github.com/user-attachments/assets/721c3d1f-d89e-4b5e-b888-f862b5e59229" />


## 🚀 Getting Started

### Prerequisites

- Node.js (v16 or later)
- Python 3.8+
- pip (Python package manager)
- Milvus database (for vector search)
- Meta's SAM2 model (for segmentation tasks)

### Frontend Setup (i-vision-frontend)

1. Navigate to the frontend directory:
   ```bash
   cd i-vision-frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   ng serve
   ```

4. Open your browser and navigate to `http://localhost:4200`

### Backend Setup (i-vision-backend)

1. Navigate to the backend directory:
   ```bash
   cd i-vision-backend
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up Milvus Vector Database:
   - Install Docker if not already installed
   - Run Milvus using Docker:
     ```bash
     docker run -d --name milvus_cpu \
     -p 19530:19530 \
     -p 9091:9091 \
     milvusdb/milvus:latest
     ```

5. Download required models:
   - Download SAM2 model
   - Download Grounding DINO model and config

6. Start the FastAPI server:
   ```bash
   uvicorn controller:app --reload
   ```

## 🛠️ Project Structure

```
.
├── i-vision-frontend/                     # Frontend (Angular)
│   ├── src/                    # Source files
│   │   ├── app/               # Angular components and services
│   │   └── assets/            # Static assets
│   └── angular.json           # Angular configuration
│
└── i-vision-backend/                    # Backend (FastAPI)
    ├── controller.py          # API endpoints and request handling
    ├── gemma3.py             # Google Gemini/Gemma model integration
    ├── milvusdb.py           # Milvus vector database operations
    ├── grounding_dino/       # Grounding DINO model files
    │   ├── config.py
    │   └── model.py
    ├── sam2/                 # Meta SAM2 model implementation
    │   ├── predictor.py
    │   └── model.py
    ├── requirements.txt      # Python dependencies
    └── .env.example         # Environment configuration template
```

## 🔧 API Documentation

This project uses FastAPI's built-in OpenAPI (Swagger) documentation, which provides interactive API documentation and testing capabilities.

### Accessing the API Documentation

1. **Development Server**:
   - Start the FastAPI server (if not already running):
     ```bash
     cd i-vision-backend
     uvicorn controller:app --reload
     ```
   - Open your browser and navigate to:
     - **Swagger UI**: http://localhost:8000/docs
     - **ReDoc**: http://localhost:8000/redoc

## 🙏 Acknowledgments

- Meta AI for the SAM2 model
- Angular and FastAPI communities
- All open-source contributors

---

<div align="center">
  Made with ❤️ for intelligent vision analysis
</div>
