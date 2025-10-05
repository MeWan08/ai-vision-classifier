from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from PIL import Image
import numpy as np
import io

app = Flask(__name__)
CORS(app)

# Load pre-trained model (MobileNetV2 - lightweight for free tier)
model = MobileNetV2(weights='imagenet')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'model': 'MobileNetV2'})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        img = Image.open(io.BytesIO(file.read()))
        
        # Preprocess image
        img = img.resize((224, 224))
        img_array = np.array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        # Make prediction
        predictions = model.predict(img_array)
        decoded = decode_predictions(predictions, top=5)[0]
        
        results = [
            {'label': label, 'confidence': float(confidence)}
            for (_, label, confidence) in decoded
        ]
        
        return jsonify({
            'success': True,
            'predictions': results
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)