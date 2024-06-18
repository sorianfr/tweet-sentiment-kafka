import csv
import os

input_file = '/home/ubuntu/documents/tweet-sentiment-kafka/trumptweets.csv'

# Get the directory of the input file
input_directory = os.path.dirname(input_file)

# Define the output file template with the same directory
output_file_template = os.path.join(input_directory, 'output_file_part_{}.csv')

# Read the original file
with open(input_file, 'r', newline='') as csvfile:
    reader = list(csv.reader(csvfile))
    
    # Extract the header
    header = reader[0]
    rows = reader[1:]  # Exclude the header for splitting
    
    # Calculate the number of lines per file
    total_lines = len(rows)
    lines_per_file = total_lines // 10
    remainder = total_lines % 10
    
    # Split the file into 10 parts
    for i in range(10):
        start_index = i * lines_per_file
        end_index = start_index + lines_per_file
        if i == 9:
            # Add any remaining lines to the last file
            end_index += remainder
        
        # Write each part to a new file
        with open(output_file_template.format(i+1), 'w', newline='') as part_file:
            writer = csv.writer(part_file)
            writer.writerow(header)  # Write the header to each file
            writer.writerows(rows[start_index:end_index])

print("CSV file has been split into 10 parts.")
