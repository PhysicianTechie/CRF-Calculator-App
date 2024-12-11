import pdfplumber
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Administrative items to exclude
ADMIN_ITEMS = [
    "Informed Consent",
    "Assign subject ID",
    "Randomization",
    "AE / surgical complications collection",
    # Add other keywords as necessary
]

# Count rows and symbols
def process_pdf(file_path):
    results = {
        "unique_counts": 0,
        "complete_counts": 0,
        "row_details": []
    }

    with pdfplumber.open(file_path) as pdf:
        for page_number in [44, 45]:  # Relevant pages
            page = pdf.pages[page_number - 1]
            tables = page.extract_tables()

            if tables:
                for table in tables:
                    for row in table:
                        # Join row content for a human-readable name
                        row_name = " | ".join(str(cell) or "" for cell in row)

                        # Exclude administrative rows
                        if any(admin_item in row_name for admin_item in ADMIN_ITEMS):
                            continue

                        # Count as a unique row
                        results["unique_counts"] += 1

                        # Count black dots in the row
                        dot_count = sum(str(cell).count("•") for cell in row if cell)
                        results["complete_counts"] += dot_count

                        # Add row details
                        results["row_details"].append({
                            "row_name": row_name,
                            "dot_count": dot_count
                        })

    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    file_path = f"./uploads/{file.filename}"
    file.save(file_path)

    try:
        results = process_pdf(file_path)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
