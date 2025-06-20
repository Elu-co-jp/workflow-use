#!/usr/bin/env python3
"""
Script to normalize candidate IDs by removing leading zeros
"""
import csv
import sys
from pathlib import Path

def normalize_csv(input_file, output_file):
    """Normalize candidate IDs by removing leading zeros"""
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        # Read all rows and normalize candidate_id
        rows = []
        for row in reader:
            if 'candidateId' in row:
                # Remove leading zeros from candidateId
                row['candidateId'] = row['candidateId'].lstrip('0') or '0'
            elif 'candidate_id' in row:
                # Remove leading zeros from candidate_id
                row['candidate_id'] = row['candidate_id'].lstrip('0') or '0'
            rows.append(row)
    
    # Write normalized data
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        if rows:
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    
    print(f"Normalized {len(rows)} rows from {input_file} to {output_file}")
    
    # Show the changes
    for i, row in enumerate(rows[:5]):  # Show first 5 rows
        if 'candidateId' in row:
            print(f"Row {i+1}: candidateId = {row['candidateId']}")
        elif 'candidate_id' in row:
            print(f"Row {i+1}: candidate_id = {row['candidate_id']}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python normalize_candidate_ids.py <input_csv> <output_csv>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not Path(input_file).exists():
        print(f"Error: Input file {input_file} does not exist")
        sys.exit(1)
    
    normalize_csv(input_file, output_file)