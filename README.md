# IoT-Exploration

Starter repo for exploring ways to send messages to an Alexa device from an external service.

This repository contains a minimal Flask server skeleton that will eventually call Alexa APIs (Notifications / Proactive Events / Skill interfaces). Implementing direct TTS delivery to a device requires creating an Alexa Skill, obtaining user permissions and access tokens (Login with Amazon / LWA), and following Amazon's APIs and policies.

This first step scaffolds the project and provides a placeholder endpoint to accept messages.

Quick start

- Install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- Run the server:

```bash
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5000
```

- Send a message (placeholder):

```bash
curl -X POST http://localhost:5000/send -H "Content-Type: application/json" -d '{"message":"Hello from IoT-Exploration"}'
```

Notes / next steps

- You will need an Amazon Developer account and to create an Alexa Skill (with notifications or proactive events) or implement a user-authorized flow using Login with Amazon (LWA).
- This repo currently contains a placeholder `send_to_alexa()` implementation in `app.py`. Next steps: implement OAuth/LWA token exchange, build/enable an Alexa Skill, request device/notification permissions, and call the appropriate Alexa API to deliver the content.

