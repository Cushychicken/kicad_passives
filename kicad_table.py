import os
import argparse
import pandas as pd

# HTML template for component pages
component_html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{component_name} Table</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.4/css/jquery.dataTables.min.css">
</head>
<body>

<div class="container my-4">
    <h2 class="text-center">{component_name} Table</h2>
    <div class="table-responsive">
        {table_content}
    </div>
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

# Define columns to exclude
EXCLUDE_COLUMNS = {
    "Price", "Stock", "@ qty", "Min Qty", "Series", "Size / Dimension",
    "Number of Terminations", "Features", "Temperature Coefficient",
    "Operating Temperature", "Supplier Device Package", "Height - Seated (Max)",
    "Size / Dimension", "Composition", "Product Status", "Supplier",
    "Failure Rate", "Ratings", "Image", "Datasheet", "Applications",
    "Lead Spacing", "Lead Style", "Thickness (Max)"
}

def expand_multiple_values(row, dk_part_column="DK Part #", package_column=" Package"):
    # Split "DK Part #" and "Package" columns by commas if multiple values exist
    dk_parts = row[dk_part_column].split(",") if pd.notnull(row[dk_part_column]) else [""]
    packages = row[package_column].split(",") if pd.notnull(row[package_column]) else [""]

    # Ensure we have the same number of entries for each column by duplicating if needed
    max_len = max(len(dk_parts), len(packages))
    dk_parts = dk_parts * max_len if len(dk_parts) == 1 else dk_parts
    packages = packages * max_len if len(packages) == 1 else packages

    # Generate a row for each unique combination of DK Part # and Package
    expanded_rows = []
    for dk_part, package in zip(dk_parts, packages):
        expanded_row = row.copy()
        expanded_row[dk_part_column] = dk_part.strip()
        expanded_row[package_column] = package.strip()
        expanded_rows.append(expanded_row)

    return expanded_rows

def generate_table_from_combined_csv(df):
    # Filter out unwanted columns if they exist in the dataframe
    df = df[[col for col in df.columns if col not in EXCLUDE_COLUMNS]]
    headers = df.columns.tolist()

    # Expand rows with multiple DK Part # or Package values
    expanded_rows = []
    for _, row in df.iterrows():
        expanded_rows.extend(expand_multiple_values(row))
    expanded_df = pd.DataFrame(expanded_rows)

    # Generate the table header HTML, adding a header for the "Copy" button
    header_html = "".join([f"<th>{header}</th>" for header in headers]) + "<th>Copy</th>"

    # Generate the table rows HTML with a "Copy" button in each row
    rows_html = []
    for _, row in expanded_df.iterrows():
        # Generate a comma-separated string of all values in the row for copying
        row_values = ", ".join(str(value) for value in row)

        # Row HTML with data and the copy button
        row_html = "".join([f"<td>{value}</td>" for value in row]) + f"<td><button class='btn btn-primary btn-sm' onclick=\"copyToClipboard('{row_values}')\">Copy</button></td>"
        rows_html.append(f"<tr>{row_html}</tr>")

    table_html = f"""
    <table id="componentsTable" class="table table-striped table-bordered">
        <thead><tr>{header_html}</tr></thead>
        <tbody>{" ".join(rows_html)}</tbody>
    </table>
    """
    return table_html

def create_index_page(component_pages):
    # HTML template for the index page
    index_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Components Index</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>

    <div class="container my-4">
        <h2 class="text-center">Components Index</h2>
        <ul class="list-group">
            {links}
        </ul>
    </div>

    </body>
    </html>
    """
    # Generate list of links to component pages
    links_html = "\n".join([f'<li class="list-group-item"><a href="{page}.html">{page.title()}</a></li>' for page in component_pages])

    # Write the index page
    with open("index.html", "w") as f:
        f.write(index_html.format(links=links_html))

def main():
    parser = argparse.ArgumentParser(description="Generate separate HTML tables for each component type")
    parser.add_argument("directory", type=str, help="Main directory containing subdirectories with component CSV files")
    args = parser.parse_args()

    component_pages = []

    # Iterate over each subdirectory in the specified main directory
    for subdirectory in os.listdir(args.directory):
        subdirectory_path = os.path.join(args.directory, subdirectory)

        # Only process directories (each representing a component type)
        if os.path.isdir(subdirectory_path):
            component_name = subdirectory.replace('_', ' ').title()
            output_filename = f"{subdirectory}.html"
            component_pages.append(subdirectory)

            # Combine all CSV files in the subdirectory into a single DataFrame
            combined_df = pd.DataFrame()
            for filename in os.listdir(subdirectory_path):
                if filename.endswith('.csv'):
                    file_path = os.path.join(subdirectory_path, filename)
                    df = pd.read_csv(file_path)
                    combined_df = pd.concat([combined_df, df], ignore_index=True)

            # Generate the HTML table for the combined DataFrame with selective columns
            table_html = generate_table_from_combined_csv(combined_df)

            # Write the component HTML page
            with open(output_filename, "w") as f:
                f.write(component_html_template.format(component_name=component_name, table_content=table_html))

    # Generate the index page linking to all component HTML pages
    create_index_page(component_pages)
    print(f"Generated index.html and individual component pages.")

if __name__ == "__main__":
    main()

