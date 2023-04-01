import csv

def split_csv(input_file, output_template, num_splits):
    with open(input_file, 'r') as file:
        reader = csv.DictReader(file)
        rows = [row for row in reader]

    chunk_size = len(rows) // num_splits
    for i in range(num_splits):
        start = i * chunk_size
        end = start + chunk_size if i != num_splits - 1 else len(rows)
        chunk = rows[start:end]

        output_file = output_template.format(i)
        with open(output_file, 'w') as file:
            writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(chunk)

input_file = 'PATH_TO_CSV_FILE'
output_template = 'csv_files/split_csv_{}.csv'
num_splits = 8

split_csv(input_file, output_template, num_splits)