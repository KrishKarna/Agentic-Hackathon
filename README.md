# Agentic-Hackathon

1. AI Independence & Navigation Agent 

Problem Statement

Build an AI agent that helps a visually impaired person understand and navigate their surroundings and perform everyday tasks more independently. The system should combine visual and voice inputs, understand the user’s intent, identify relevant objects, signs, obstacles and environmental context, and decide what assistance is appropriate. 

Example Scenario 

 A user says, “Help me find the entrance to this building.” The agent interprets the request, analyses the camera view, identifies doors, signs and obstacles, determines which entrance is relevant, and provides suitable voice or haptic guidance. It should adapt as the environment changes. 

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) (required for sign reading — `pytesseract` calls out to this binary). On Windows: `winget install --id UB-Mannheim.TesseractOCR -e`.
3. Copy `.env.example` to `.env` and set `GROQ_API_KEY`.

## Running

- Desktop (OpenCV window):
  ```
  python agent-navigation/live_test.py
  ```
- Web dashboard (live camera feed + status panel in the browser, at `http://localhost:5000`):
  ```
  python agent-navigation/web_app.py
  ```

Say a command any time — the assistant listens continuously, not just once at startup:
- "check for obstacles" / "describe the scene"
- "find my bottle" / "find a chair" (searches for a specific object)
- "read this sign" / "what does it say" (reads visible text aloud via OCR)

An emergency warning ("Stop, X directly ahead") overrides whatever else is happening whenever something is centered and very close to the camera.