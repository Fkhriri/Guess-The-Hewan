# Animal Guessing Game

An interactive game where players guess animals based on descriptions. Features both click and voice input modes.

## Setup

### Prerequisites
- Python 3.8 or higher
- Node.js (for serving static files if needed)
- Modern web browser

### Backend Setup
1. Navigate to the python_backend directory:
```powershell
cd python_backend
```

2. Create a virtual environment and activate it:
```powershell
python -m venv venv
.\venv\Scripts\activate
```

3. Install required packages:
```powershell
pip install -r requirements.txt
```

### Running the Application

1. Start the Python backend server:
```powershell
cd python_backend
.\venv\Scripts\activate
python main.py
```
The server will start at http://localhost:8000

2. Open the HTML file in your web browser
- Simply open `guess-game.html` in your web browser
- Or use a simple HTTP server if needed:
```powershell
python -m http.server 8080
```

## Features

- Two game modes: Click and Voice input
- Voice recognition for Indonesian language
- Interactive UI with image reveals
- Score tracking
- Timed gameplay (60 seconds)
- Sound effects and background music

## Usage

1. Choose your preferred mode (Click or Voice)
2. Click "Start Challenge"
3. For voice mode:
   - Click the "Record" button
   - Speak "A", "B", or "C" clearly
   - Wait for processing (about 5 seconds)
4. For click mode:
   - Simply click on your chosen answer

## Technical Details

- Frontend: HTML, CSS, JavaScript
- Backend: Python with FastAPI
- Speech Recognition: Google Speech Recognition API
- Logging: Loguru for comprehensive logging
- Audio Processing: Wave and NumPy for audio handling
