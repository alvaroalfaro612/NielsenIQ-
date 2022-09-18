from io import BytesIO

from flask import Flask, request, jsonify

from counter import config

app = Flask(__name__)
count_action = config.get_count_action()

@app.route('/object-count', methods=['POST'])
def object_detection():
    uploaded_file = request.files['file']
    threshold = float(request.form.get('threshold', 0.5))
    image = BytesIO()
    uploaded_file.save(image)
    count_response = count_action.execute(image, threshold)
    return jsonify(count_response)

@app.route('/detection-list', methods=['POST']) #returns a list with the predictions given an image and a threshold
def detection_list():
    uploaded_file = request.files['file']
    threshold = float(request.form.get('threshold', 0.5))
    image = BytesIO()
    uploaded_file.save(image)
    detection_list = count_action.get_predictions_list(image, threshold)
    return jsonify(detection_list)

@app.route('/api-status', methods=['GET']) 
def api_status():
    return jsonify("Flask API is working")

if __name__ == '__main__':
    app.run('0.0.0.0', port=6010, debug=False)
