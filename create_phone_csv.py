import json
import csv
import os

def create_companies_with_phones_csv():
    """Create CSV file with only companies that have phone numbers"""
    
    # Check for different possible input files
    possible_files = [
        'companies_with_phones_enhanced.json',
        'companies_with_phones.json',
        'test_results.json'
    ]
    
    input_file = None
    for file in possible_files:
        if os.path.exists(file):
            input_file = file
            break
    
    if not input_file:
        print("No processed phone data found. Please run the phone search agent first.")
        return
    
    print(f"Loading data from: {input_file}")
    
    # Load the data
    with open(input_file, 'r', encoding='utf-8') as f:
        companies_data = json.load(f)
    
    # Filter companies with phone numbers
    companies_with_phones = []
    for company in companies_data:
        phone = company.get('phone')
        if phone and phone.strip() and phone != 'Not found':
            companies_with_phones.append(company)
    
    if not companies_with_phones:
        print("No companies with phone numbers found in the data.")
        return
    
    # Define CSV columns
    csv_columns = [
        'company_name',
        'phone',
        'address',
        'postal_code',
        'municipality',
        'province',
        'business_purpose',
        'social_capital',
        'start_date',
        'coordinates',
        'url'
    ]
    
    # Create CSV file
    output_file = 'companies_with_phones.csv'
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        
        # Write header
        writer.writeheader()
        
        # Write data
        for company in companies_with_phones:
            # Create row with only the columns we want
            row = {}
            for col in csv_columns:
                row[col] = company.get(col, '')
            writer.writerow(row)
    
    print(f"✓ Created {output_file}")
    print(f"✓ Total companies with phones: {len(companies_with_phones)}")
    print(f"✓ Out of {len(companies_data)} total companies")
    print(f"✓ Success rate: {len(companies_with_phones)/len(companies_data)*100:.1f}%")

if __name__ == "__main__":
    create_companies_with_phones_csv()