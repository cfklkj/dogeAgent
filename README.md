# dogeAgent - Desktop Pet AI Agent

A cute Shiba Inu desktop pet powered by LangChain and NVIDIA AI.

## Features

- 🐕 Cute Shiba Inu (Doge) desktop pet
- 🤖 AI-powered conversations using NVIDIA z-ai/glm5
- 🛠️ Built-in tools: time, date, calculator
- 💬 Chat panel with quick actions
- 🎨 Transparent desktop window

## Tech Stack

- **Frontend**: Electron (transparent window)
- **Backend**: Python + LangChain v1.0
- **AI Model**: NVIDIA z-ai/glm5 (default)

## Quick Start

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env and add your NVIDIA_API_KEY

# Run the app
npm start
```

## Project Structure

```
dogeAgent/
├── electron/          # Electron frontend
├── agent/             # Agent factory
├── tools/             # Tool system
├── models/            # Model config
├── desktop/           # Bridge service
├── config/            # Settings
├── assets/            # Icons and images
└── tests/             # Test files
```

## License

MIT
