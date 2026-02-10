import csv


def update_first_row_in_csv(csv_path, updated_values):
    """
    Read a CSV file and change the first data row with new values.

    Args:
        csv_path: Path to the CSV file
        updated_values: Dictionary with column names as keys and new values
    """
    # Read the CSV file
    with open(csv_path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    # Update the first row with new values
    if rows:
        for key, value in updated_values.items():
            if key in rows[0]:
                rows[0][key] = value

    # Write back to the CSV file
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return rows[0]
