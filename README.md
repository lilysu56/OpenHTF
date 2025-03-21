# OpenHTF Test Results Exporter

This project contains a Python script `export_results.py` used to convert OpenHTF test results from JSON format to HTML format, making it easy to view and share.

## Features

- Supports reading JSON files from multiple subdirectories
- Converts test results into a visually appealing HTML file
- Provides a device ID selector to filter displayed test results
- Supports viewing detailed information and logs for test phases

## Installation

Make sure you have Python 3 and `pip` installed. You can install the required dependencies with the following command:

```bash
pip install -r requirements.txt

Usage
Organize the JSON files containing OpenHTF test results into the specified directory.
Execute the script using the following command, specifying the input directory and the output HTML file path:
bash
python export_results.py --input-dir path/to/json/results --output-file output.html

Command Line Arguments
--input-dir: Directory containing JSON test results. Default is ~/AppData/Local/tackv/spintop-openhtf/openhtf-history/examples.hello_world.
--output-file: Path to the output HTML file. Default is test_results.html.
Example
Assuming you have a directory ~/test_results containing test results and you want to export them to results.html, you can use the following command:

bash
python export_results.py --input-dir ~/test_results --output-file results.html
Once executed, you will find the generated HTML file at the specified output path.
