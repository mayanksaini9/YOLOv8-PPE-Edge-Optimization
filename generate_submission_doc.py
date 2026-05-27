import os

def main():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YOLOv8 Edge Optimization Submission Document</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        :root {
            --primary: #4F46E5;
            --primary-hover: #4338CA;
            --bg: #F9FAFB;
            --card-bg: #FFFFFF;
            --text-main: #111827;
            --text-muted: #4B5563;
            --border: #E5E7EB;
            --success: #10B981;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            margin: 0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
        }

        .container {
            max-width: 800px;
            width: 100%;
            background-color: var(--card-bg);
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border: 1px solid var(--border);
            padding: 40px;
            box-sizing: border-box;
        }

        header {
            border-bottom: 2px solid var(--border);
            padding-bottom: 20px;
            margin-bottom: 30px;
            text-align: center;
        }

        h1 {
            color: var(--primary);
            font-size: 28px;
            font-weight: 700;
            margin: 0 0 10px 0;
        }

        .subtitle {
            color: var(--text-muted);
            font-size: 16px;
            margin: 0;
        }

        .section {
            margin-bottom: 35px;
        }

        h2 {
            font-size: 20px;
            font-weight: 600;
            border-left: 4px solid var(--primary);
            padding-left: 10px;
            margin-bottom: 15px;
        }

        .input-group {
            margin-bottom: 15px;
        }

        label {
            display: block;
            font-weight: 500;
            margin-bottom: 5px;
            font-size: 14px;
        }

        input[type="text"], input[type="url"] {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 14px;
            box-sizing: border-box;
            background-color: #F3F4F6;
            color: var(--text-main);
        }

        input[type="text"]:focus, input[type="url"]:focus {
            outline: none;
            border-color: var(--primary);
            background-color: #FFFFFF;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }

        th, td {
            border: 1px solid var(--border);
            padding: 12px;
            text-align: left;
        }

        th {
            background-color: #F3F4F6;
            font-weight: 600;
        }

        tr:nth-child(even) td {
            background-color: #F9FAFB;
        }

        .badge {
            background-color: #EEF2FF;
            color: var(--primary);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }

        .badge-green {
            background-color: #ECFDF5;
            color: var(--success);
        }

        .btn-container {
            display: flex;
            justify-content: center;
            margin-top: 30px;
            gap: 15px;
        }

        button {
            background-color: var(--primary);
            color: #FFFFFF;
            border: none;
            padding: 12px 24px;
            font-size: 15px;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        button:hover {
            background-color: var(--primary-hover);
        }

        .btn-secondary {
            background-color: #6B7280;
        }

        .btn-secondary:hover {
            background-color: #555861;
        }

        .instructions {
            background-color: #FFFBEB;
            border: 1px solid #FDE68A;
            border-radius: 8px;
            padding: 15px;
            font-size: 13px;
            color: #92400E;
            margin-bottom: 25px;
        }

        @media print {
            body {
                background-color: #FFFFFF;
                padding: 0;
            }
            .container {
                box-shadow: none;
                border: none;
                padding: 0;
            }
            .btn-container, .instructions, .edit-mode-only {
                display: none !important;
            }
            input[type="text"], input[type="url"] {
                border: none;
                background-color: transparent;
                padding: 0;
                font-size: 16px;
                font-weight: bold;
                color: var(--primary);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>YOLOv8 Edge Optimization & Benchmarking</h1>
            <p class="subtitle">Industrial PPE / Hard Hat Detection Assignment Submission</p>
        </header>

        <div class="instructions">
            <strong>📝 Submission Instructions:</strong> Fill in your student details and project URLs below. Once filled, click the <strong>"Export to PDF"</strong> button to save this page as a PDF file, which is ready to upload for your submission.
        </div>

        <div class="section">
            <h2>👤 Submitter Details</h2>
            <div class="input-group">
                <label for="student-name">Student / Developer Name:</label>
                <input type="text" id="student-name" placeholder="Enter your full name" value="Mayank">
            </div>
            <div class="input-group">
                <label for="student-email">Email Address:</label>
                <input type="text" id="student-email" placeholder="Enter your email address">
            </div>
        </div>

        <div class="section">
            <h2>🔗 Project Deliverable Links</h2>
            <div class="input-group">
                <label for="github-url">GitHub Repository Link:</label>
                <input type="url" id="github-url" placeholder="https://github.com/username/repository">
            </div>
            <div class="input-group">
                <label for="weights-url">Model Weights Link (Cloud Folder):</label>
                <input type="url" id="weights-url" placeholder="https://drive.google.com/drive/folders/...">
            </div>
            <div class="input-group">
                <label for="video-url">Video Demonstration Link (YouTube/Drive):</label>
                <input type="url" id="video-url" placeholder="https://www.youtube.com/watch?v=...">
            </div>
        </div>

        <div class="section">
            <h2>📊 Performance Benchmarking Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>Model Format</th>
                        <th>Physical Size (MB)</th>
                        <th>Size Reduction</th>
                        <th>Accuracy (mAP50)</th>
                        <th>Local Speed (FPS)</th>
                        <th>Avg Latency</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>PyTorch FP32 (Baseline)</strong></td>
                        <td>5.9 MB</td>
                        <td><span class="badge">Baseline</span></td>
                        <td>0.380</td>
                        <td>29.02 FPS</td>
                        <td>~34.4 ms</td>
                    </tr>
                    <tr>
                        <td><strong>ONNX FP32 (Converted)</strong></td>
                        <td>11.6 MB</td>
                        <td>+96.6%</td>
                        <td>0.380</td>
                        <td>57.37 FPS</td>
                        <td>~17.4 ms</td>
                    </tr>
                    <tr>
                        <td><strong>ONNX FP16 (Quantized)</strong></td>
                        <td>5.8 MB</td>
                        <td><span class="badge badge-green">-50.3% (vs FP32)</span></td>
                        <td>0.380</td>
                        <td>53.37 FPS</td>
                        <td>~18.7 ms</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>💡 Core Findings & Edge Optimization Insights</h2>
            <ul>
                <li><strong>ONNX CPU Speedup:</strong> Converting the baseline PyTorch model to ONNX format yielded a **~1.97x speedup** on local CPU execution, raising the framerate from 29.02 FPS to **57.37 FPS**, satisfying real-time inference constraints.</li>
                <li><strong>FP16 Quantization Impact:</strong> Quantization to FP16 half-precision successfully halved the storage footprint of the ONNX model (shrinking it from **11.6 MB to 5.8 MB**), resolving memory bottlenecks for deployment on edge devices.</li>
                <li><strong>Accuracy Preservation:</strong> Benchmarks confirm zero accuracy degradation (retaining **0.380 mAP50**) during conversion and half-precision quantization.</li>
            </ul>
        </div>

        <div class="btn-container">
            <button onclick="window.print()">Export to PDF</button>
        </div>
    </div>
</body>
</html>
"""
    with open("submission_document.html", "w", encoding="utf-8") as f:
        f.write(html_content.strip())
    print("Created submission_document.html successfully!")

if __name__ == "__main__":
    main()
