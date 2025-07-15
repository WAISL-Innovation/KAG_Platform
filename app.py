import sys
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import os
import re
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from src.kag_platform.pipeline.kag_query_processing_pipeline import KagQueryProcessingPipeline


app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)



from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import re

@app.route('/kag_chat', methods=['GET', 'POST'])
def kag_chat():
    answer = None

    if request.method == 'POST':
        # Support both form data and raw JSON
        if request.is_json:
            question = request.json.get('question', '').strip()
        else:
            question = request.form.get('question', '').strip()

        if not question:
            message = "Please enter a question."
            if request.is_json:
                return jsonify({"error": message}), 400
            flash(message, "danger")
            return redirect(url_for('kag_chat'))

        if not re.match(r'^[\w\s\?\.,-]+$', question):
            message = "Invalid characters in question."
            if request.is_json:
                return jsonify({"error": message}), 400
            flash(message, "danger")
            return redirect(url_for('kag_chat'))

        try:
            kag_conversation = KagQueryProcessingPipeline()
            answer = kag_conversation.process_query(question)

        except Exception as e:
            message = f"Error retrieving answer: {e}"
            if request.is_json:
                return jsonify({"error": message}), 500
            flash(message, "danger")
            return redirect(url_for('kag_chat'))

        # ✅ JSON Response for Postman
        if request.is_json:
            return jsonify({"answer": answer})

    # ✅ HTML page rendering
    return render_template('graph_kag.html', answer=answer)


@app.route('/upload_kag', methods=['GET', 'POST'])
def upload_kag():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'message': 'No file part'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400

        if not file.filename.lower().endswith(('.pdf', '.txt', '.docx')):
            return jsonify({'message': 'Unsupported file type'}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        try:
            file.save(file_path)
            kag_conversation = KagQueryProcessingPipeline()
            response = kag_conversation.data_ingestion(file_path)
            if "inserted successfully" in response:
                return jsonify({'message': 'File uploaded and processed successfully'}), 200
            return jsonify({'message': response}), 400
        except Exception as e:
            return jsonify({'message': str(e)}), 500
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    return render_template('kag_upload.html')


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=8080)
