import os
import argparse
import pandas as pd

# HTML template with placeholders for table rows
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Components Table</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.4/css/jquery.dataTables.min.css">
</head>
<body>

<div class="container my-4">
    <h2 class="text-center">Components Table</h2>
    <table id="componentsTable" class="table table-striped table-bordered">
        <thead>
            <tr>
                <th>DK Part #</th>
                <th>Mfr Part #</th>
                <th>Mfr</th>
                <th>Description</th>
                <th>Package</th>
                <th>Value</th>
                <th>Tolerance</th>
                <th>Voltage - Rated</th>
                <th>Package / Case</th>
                <th>Copy</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
</div>

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
<script>
    $(document).ready(function() {{
        $('#componentsTable').DataTable();
    }});

    function copyToClipboard(text) {{
        // Split the input text by commas, then join by tabs
        const tabDelimitedText = text.split(',').map(item => item.trim()).join('\\t');

        // Write the tab-delimited text to the clipboard
        navigator.clipboard.writeText(tabDelimitedText).then(function() {{
            alert('Copied to clipboard: ' + tabDelimitedText);
        }}, function(err) {{
            console.error('Could not copy text: ', err);
        }});
    }}
</script>

</body>
</html>
"""

def generate_table_rows_from_csv(file_path):
    columns = [
        'DK Part #', 'Mfr Part #', 'Mfr', 'Description',
        ' Package', 'Capacitance', 'Tolerance',
        'Voltage - Rated', 'Package / Case'
    ]

    try:
        df = pd.read_csv(file_path, usecols=columns)
        df = df.fillna('')

        rows = []
        for _, row in df.iterrows():
            dk_parts = row['DK Part #'].split(",")  # Split multiple DK Part # values
            packages = row[' Package'].split(",")   # Split multiple Package values

            # Ensure we have the same number of DK parts and package entries if possible
            if len(dk_parts) != len(packages):
                # In case of mismatch, duplicate the single value to match the other's length or use first value
                if len(dk_parts) < len(packages):
                    dk_parts *= len(packages)
                elif len(packages) < len(dk_parts):
                    packages *= len(dk_parts)

            mfr_part = row['Mfr Part #']
            mfr = row['Mfr']
            description = row['Description']
            capacitance = row['Capacitance']
            tolerance = row['Tolerance']
            voltage = row['Voltage - Rated']
            package_case = row['Package / Case']

            # Create a row for each DK Part # and Package combination
            for dk_part, package in zip(dk_parts, packages):
                dk_part = dk_part.strip()
                package = package.strip()
                clipboard_text = f"Digikey, {dk_part}, {mfr}, {mfr_part}"

                copy_button_html = f"""<button class="btn btn-primary btn-sm" onclick="copyToClipboard('{clipboard_text}')">Copy</button>"""

                row_html = f"<tr><td>{dk_part}</td><td>{mfr_part}</td><td>{mfr}</td><td>{description}</td><td>{package}</td><td>{capacitance}</td><td>{tolerance}</td><td>{voltage}</td><td>{package_case}</td><td>{copy_button_html}</td></tr>"
                rows.append(row_html)

        return "\n".join(rows)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return ""

def main():
    parser = argparse.ArgumentParser(description="Generate an HTML table from CSV files in a directory")
    parser.add_argument("directory", type=str, help="Directory containing CSV files")
    parser.add_argument("-o", "--output", type=str, default="index.html", help="Output HTML file name (default: index.html)")
    args = parser.parse_args()

    all_rows = []
    for filename in os.listdir(args.directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(args.directory, filename)
            all_rows.append(generate_table_rows_from_csv(file_path))

    final_html = html_template.format(table_rows="\n".join(all_rows))

    with open(args.output, 'w') as file:
        file.write(final_html)

    print(f"Generated HTML file: {args.output}")

if __name__ == "__main__":
    main()

