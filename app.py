import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from googletrans import Translator, LANGUAGES

# --------------------
# Load Environment Variables
# --------------------
load_dotenv()  # Loads .env file

ACCESS_SECRET = os.getenv("ACCESS_SECRET", "default_access_secret")
REFRESH_SECRET = os.getenv("REFRESH_SECRET", "default_refresh_secret")


# --------------------
# Flask App Setup
# --------------------
app = Flask(__name__)
CORS(app)



# Initialize extensions
translator = Translator()

# --------------------
# Import JWT Auth Functions
# --------------------
from auth import (
    generate_access_token,
    generate_refresh_token,
    verify_refresh_token,
    remove_refresh_token,
    token_required
)

# --------------------
# Database Model
# --------------------


# --------------------
# Language Validity Check
# --------------------
def valid_lang(lang_code):
    return lang_code in LANGUAGES

# --------------------
# Routes
# --------------------
@app.route('/')
def index():
   
    return render_template('index.html', languages=LANGUAGES,)

@app.route('/about')
def about():
    return render_template('about.html', languages=LANGUAGES)

@app.route('/contact')
def contact():
    return render_template('contact.html', languages=LANGUAGES)

@app.route('/view-cv')
def view_cv():
    return render_template('cv.html', languages=LANGUAGES)

# 🔐 Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    if not username:
        return jsonify({'error': 'Username is required'}), 400

    return jsonify({
        'accessToken': generate_access_token(username),
        'refreshToken': generate_refresh_token(username)
    })

# 🔄 Refresh Token
@app.route('/token', methods=['POST'])
def refresh_token():
    data = request.get_json()
    token = data.get('token')

    if not token:
        return jsonify({'error': 'Refresh token is required'}), 400

    username = verify_refresh_token(token)
    if not username:
        return jsonify({'error': 'Invalid or expired refresh token'}), 403

    return jsonify({'accessToken': generate_access_token(username)})

# 🚪 Logout
@app.route('/logout', methods=['DELETE'])
def logout():
    data = request.get_json()
    token = data.get('token')

    if not token:
        return jsonify({'error': 'Refresh token required'}), 400

    remove_refresh_token(token)
    return '', 204

# 🔐 Protected Route
@app.route('/protected', methods=['GET'])
@token_required
def protected():
    username = getattr(request, 'username', None)
    if not username:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'message': f'Hello {username}, this is a protected route!'}), 200

# 🌍 Translation
@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json(force=True, silent=True)
    # Batch translation support
    if data and "texts" in data:
        texts = data["texts"]
        target = data.get("target", "en").lower()
        if not valid_lang(target):
            return jsonify({
                "error": f"Unsupported language '{target}'. Supported: {', '.join(sorted(LANGUAGES.keys()))}"
            }), 400
        try:
            translated = {}
            for key, text in texts.items():
                result = translator.translate(text, dest=target)
                translated[key] = result.text
            return jsonify({"translated": translated})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    # Single text translation (legacy)
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field"}), 400

    text = data["text"]
    target = data.get("target", "en").lower()

    if not valid_lang(target):
        return jsonify({
            "error": f"Unsupported language '{target}'. Supported: {', '.join(sorted(LANGUAGES.keys()))}"
        }), 400

    try:
        result = translator.translate(text, dest=target)
        return jsonify({
            "original_text": text,
            "translated_text": result.text,
            "src_lang": result.src,
            "target_lang": target
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 👤 Add User
@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()
    name = data.get('name')
    age = data.get('age')
    mobile = data.get('mobile_number')

    if not all([name, age, mobile]):
        return jsonify({'error': 'All fields (name, age, mobile_number) are required'}), 400

    new_user = User(name=name, age=age, mobile_number=mobile)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User added', 'user': new_user.to_dict()}), 201

# 📋 Get Users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200

# --------------------
# Run App
# --------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)
