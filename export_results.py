import json
import os
from html import escape
from datetime import datetime
import time
import argparse

def format_duration(milliseconds):
    """Convert milliseconds to human readable time format"""
    seconds = milliseconds / 1000
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{int(minutes)}m {int(seconds)}s"

def convert_results_to_html(results):
    print("Entering convert_results_to_html")
    # 獲取所有不重複的設備ID
    device_ids = sorted(set(result.get('dut_id', '01') for result in results))
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OpenHTF Test Results</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .test-block {
                background-color: white;
                margin-bottom: 20px;
                border-radius: 4px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            }
            .test-header {
                padding: 15px;
                border-bottom: 1px solid #eee;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
            }
            .test-header h2 {
                margin: 0;
                grid-column: 1 / -1;
                color: #333;
            }
            .header-item {
                display: flex;
                flex-direction: column;
            }
            .header-item label {
                font-size: 0.9em;
                color: #666;
                margin-bottom: 5px;
            }
            .header-item .value {
                font-weight: bold;
            }
            .status {
                display: inline-block;
                padding: 3px 8px;
                border-radius: 3px;
                color: white;
                font-weight: bold;
            }
            .status-PASS { background-color: #00c853; }
            .status-FAIL { background-color: #ff1744; }
            .phase-table {
                width: 100%;
                border-collapse: collapse;
                margin: 0;
            }
            .phase-table th, .phase-table td {
                padding: 8px 15px;
                text-align: left;
                border-bottom: 1px solid #eee;
            }
            .phase-table th {
                background-color: #f8f9fa;
                font-weight: bold;
            }
            .phase-details {
                display: none;
                padding: 15px;
                background: #f8f9fa;
                border-left: 4px solid #2196f3;
                margin: 0 15px 15px;
            }
            .toggle-button {
                background: #2196f3;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                cursor: pointer;
                font-size: 0.9em;
            }
            .toggle-button:hover {
                background: #1976d2;
            }
            .log-section {
                padding: 15px;
                border-top: 1px solid #eee;
            }
            .log-filters {
                margin-bottom: 10px;
            }
            .log-entry {
                padding: 5px;
                border-bottom: 1px solid #eee;
                font-family: monospace;
                font-size: 0.9em;
            }
            .log-info { color: #2196f3; }
            .log-warning { color: #ff9800; }
            .log-error { color: #f44336; }
            .log-debug { color: #757575; }
            .device-selector {
                background: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 4px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            }
            
            .device-selector select {
                padding: 8px;
                border-radius: 4px;
                border: 1px solid #ddd;
                margin-left: 10px;
            }
            
            .test-block {
                display: none;  /* 預設隱藏所有測試塊 */
            }
            
            .test-block.active {
                display: block;  /* 顯示被選中的測試塊 */
            }
        </style>
        <script>
            function filterByDevice(deviceId) {
                // 隱藏所有測試塊
                const allTests = document.getElementsByClassName('test-block');
                for (let test of allTests) {
                    test.classList.remove('active');
                }
                
                // 顯示選中設備的測試塊
                if (deviceId) {
                    const deviceTests = document.getElementsByClassName('device-' + deviceId);
                    for (let test of deviceTests) {
                        test.classList.add('active');
                    }
                }
            }
            
            function togglePhaseDetails(phaseId) {
                const details = document.getElementById(phaseId);
                const allDetails = document.getElementsByClassName('phase-details');
                
                // Close all other details first
                for (let detail of allDetails) {
                    if (detail.id !== phaseId) {
                        detail.style.display = 'none';
                    }
                }
                
                // Toggle the clicked detail
                if (details.style.display === 'none' || details.style.display === '') {
                    details.style.display = 'block';
                } else {
                    details.style.display = 'none';
                }
            }
            
            function filterLogs(selectElement) {
                const testBlock = selectElement.closest('.test-block');
                const level = selectElement.value;
                const logs = testBlock.getElementsByClassName('log-entry');
                for (let log of logs) {
                    if (level === 'all' || log.classList.contains('log-' + level)) {
                        log.style.display = 'block';
                    } else {
                        log.style.display = 'none';
                    }
                }
            }
        </script>
    </head>
    <body>
        <div class="device-selector">
            <label for="deviceSelect">Select Device ID:</label>
            <select id="deviceSelect" onchange="filterByDevice(this.value)">
                <option value="">Select a device...</option>
    """
    
    # 添加設備ID選項
    for device_id in device_ids:
        html_content += f'<option value="{device_id}">{device_id}</option>'
    
    html_content += """
            </select>
        </div>
    """

    for test_index, result in enumerate(results):
        test_name = result.get('test_name', 'Unknown Test')
        status = result.get('status', 'UNKNOWN')
        start_time = result.get('start_time_millis', 0)
        end_time = result.get('end_time_millis', 0)
        duration = end_time - start_time if end_time and start_time else 0
        device_id = result.get('dut_id', '01')  # 獲取設備ID
        
        # 為每個測試塊添加設備ID的class
        html_content += f"""
        <div class="test-block device-{device_id}">
            <div class="test-header">
                <h2>{escape(test_name)}</h2>
                <div class="header-item">
                    <label>Device ID</label>
                    <div class="value">{device_id}</div>
                </div>
                <div class="header-item">
                    <label>Test Station</label>
                    <div class="value">AN990165152</div>
                </div>
                <div class="header-item">
                    <label>Test Result</label>
                    <div class="value">
                        <span class="status status-{status}">{status}</span>
                    </div>
                </div>
                <div class="header-item">
                    <label>Duration</label>
                    <div class="value">{format_duration(duration)}</div>
                </div>
            </div>

            <table class="phase-table">
                <tr>
                    <th>Phase Name</th>
                    <th>Result</th>
                    <th>Duration</th>
                    <th>Action</th>
                </tr>
        """

        phases = result.get('phases', [])
        for i, phase in enumerate(phases):
            phase_name = phase.get('name', 'Unknown Phase')
            phase_status = phase.get('status', 'UNKNOWN')
            phase_start = phase.get('start_time_millis', 0)
            phase_end = phase.get('end_time_millis', 0)
            phase_duration = phase_end - phase_start if phase_end and phase_start else 0
            
            # Create a unique ID for each phase using both test_index and phase index
            phase_id = f"phase_test_{test_index}_phase_{i}"
            
            html_content += f"""
                <tr>
                    <td>{escape(phase_name)}</td>
                    <td><span class="status status-{phase_status}">{phase_status}</span></td>
                    <td>{format_duration(phase_duration)}</td>
                    <td>
                        <button class="toggle-button" onclick="togglePhaseDetails('{phase_id}')">
                            Details
                        </button>
                    </td>
                </tr>
                <tr>
                    <td colspan="4">
                        <div id="{phase_id}" class="phase-details">
                            <h4>Phase Description</h4>
                            <p>{phase.get('description', 'No description available')}</p>
                            <h4>Measurements</h4>
                            <pre>{escape(json.dumps(phase.get('measurements', {}), indent=2))}</pre>
                        </div>
                    </td>
                </tr>
            """

        html_content += """
            </table>
            <div class="log-section">
                <h3>Test Logs</h3>
                <div class="log-filters">
                    <label for="logLevel">Log Level:</label>
                    <select onchange="filterLogs(this)">
                        <option value="all">All</option>
                        <option value="info">Info</option>
                        <option value="warning">Warning</option>
                        <option value="error">Error</option>
                        <option value="debug">Debug</option>
                    </select>
                </div>
        """

        logs = result.get('logs', [])
        for log in logs:
            log_time = datetime.fromtimestamp(log.get('timestamp', 0)/1000).strftime('%Y-%m-%d %H:%M:%S')
            log_level = log.get('level', 'INFO').lower()
            log_message = log.get('message', '')
            
            html_content += f"""
                <div class="log-entry log-{log_level}">
                    [{log_time}] [{log_level.upper()}] {escape(log_message)}
                </div>
            """

        html_content += """
            </div>
        </div>
        """

    html_content += """
    </body>
    </html>
    """
    return html_content

def export_results_to_html_file(results, output_file):
    """將測試結果導出為HTML檔案"""
    html_content = convert_results_to_html(results)
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(html_content)
    return output_file

def read_json_from_subdirectories(parent_directory):
    """從指定目錄及其子目錄讀取JSON檔案"""
    all_results = []
    if not os.path.exists(parent_directory):
        print(f"Directory does not exist: {parent_directory}")
        return all_results
        
    for folder_name in os.listdir(parent_directory):
        folder_path = os.path.join(parent_directory, folder_name)
        if os.path.isdir(folder_path):
            try:
                json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
                if json_files:
                    json_file_path = os.path.join(folder_path, json_files[0])
                    with open(json_file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        if isinstance(data, list):
                            all_results.extend(data)
                        else:
                            all_results.append(data)
            except Exception as e:
                print(f"Error reading JSON in {folder_name}: {e}")
    return all_results

def main():
    # 使用命令列參數來取代硬編碼的路徑
    parser = argparse.ArgumentParser(description='Convert OpenHTF JSON results to HTML')
    parser.add_argument(
        '--input-dir',
        default=os.path.join(
            os.path.expanduser('~'),
            'AppData', 'Local', 'tackv', 'spintop-openhtf', 
            'openhtf-history', 'examples.hello_world'
        ),
        help='Directory containing JSON test results'
    )
    parser.add_argument(
        '--output-file',
        default='test_results.html',
        help='Output HTML file path'
    )
    
    args = parser.parse_args()
    
    # 檢查輸入目錄並讀取 JSON
    results = read_json_from_subdirectories(args.input_dir)
    
    if results:
        output_path = export_results_to_html_file(results, args.output_file)
        print(f"HTML conversion completed, output saved as {os.path.abspath(output_path)}")
    else:
        print("No JSON test results found in the specified directory")

if __name__ == "__main__":
    main()