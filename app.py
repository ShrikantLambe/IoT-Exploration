from flask import Flask, request, jsonify
import os

app = Flask(__name__)


def send_to_alexa(message: str):
    """
    Placeholder function to send `message` to an Alexa device.

    Real implementation notes:
    - Obtain an access token via Login with Amazon (LWA) for the user/device.
    - Use the Alexa Notifications or Proactive Events APIs, or implement a Skill
      that can deliver TTS or a notification to the user's enabled device.
    - This will require creating an Alexa Skill, requesting permissions, and
      following Amazon's developer docs and policies.
    """
    raise NotImplementedError("Implement Alexa API call here. See README.md for next steps")


@app.route('/send', methods=['POST'])
def send():
    data = request.get_json(silent=True) or {}
    message = data.get('message')
    if not message:
        return jsonify({"error": "missing 'message'"}), 400
    try:
        send_to_alexa(message)
        return jsonify({"status": "queued"}), 202
    except NotImplementedError as e:
        return jsonify({"error": str(e)}), 501
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
