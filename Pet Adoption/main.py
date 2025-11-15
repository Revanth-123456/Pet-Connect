from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
from PIL import Image
import io

app = FastAPI()

# ✅ Allow frontend (React) and Node backend to access FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# EMOTION MODEL SIMULATION (replace with your CNN or model)
# -------------------------------------------------------------------
EMOTIONS = ["Angry", "Happy", "Relaxed", "Sad"]

def dummy_predict(image: Image.Image):
    """
    Simulate a neural network emotion prediction.
    Replace this with your real trained model prediction.
    """
    # Generate random probabilities
    probs = np.random.dirichlet(np.ones(len(EMOTIONS)), size=1)[0]
    top_index = int(np.argmax(probs))
    predicted_emotion = EMOTIONS[top_index]
    return predicted_emotion, probs.tolist()

# -------------------------------------------------------------------
# ROUTE: Emotion prediction endpoint
# -------------------------------------------------------------------
@app.post("/predict/")
async def predict_emotion(file: UploadFile = File(...)):
    try:
        # Validate file type
        if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
            raise HTTPException(status_code=400, detail="Invalid image type")

        # Read and preprocess the image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        # Perform prediction (replace with real model inference)
        emotion, probabilities = dummy_predict(image)

        # Return structured JSON
        return {
            "emotion": emotion,
            "probabilities": [probabilities],
            "filename": file.filename,
        }

    except Exception as e:
        print("Prediction error:", e)
        raise HTTPException(status_code=500, detail="Prediction failed")

# -------------------------------------------------------------------
# Optional Health Check Route
# -------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Emotion Prediction API is running"}
