import csv

# Read the TSV file
file_path = 'data.tsv'
with open(file_path, 'r', newline='', encoding='utf-8') as file:
    reader = list(csv.reader(file, delimiter='\t'))

# Assuming the first row is the header
header = reader[0]
data = reader[1:]

# Determine the indices of columns
disembarked_index = header.index("Disembarked")
embarked_index = header.index("Embarked")

# Process only the last 250 items
processed_data = data[-250:]

# Divide by 300 and apply minus sign only for Disembarked
for row in processed_data:
    try:
        row[disembarked_index] = -float(row[disembarked_index]) / 400
    except ValueError:
        row[disembarked_index] = 0

    try:
        row[embarked_index] = float(row[embarked_index]) / 400
    except ValueError:
        row[embarked_index] = 0

# Output processed data (you could also save this to a new file)
for row in [header] + processed_data:
    print('\t'.join(map(str, row)))
