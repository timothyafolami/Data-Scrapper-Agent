#!/usr/bin/env python3
"""
Test script for the phone search agent
Tests with a small sample of companies first
"""

import json
from enhanced_phone_agent import EnhancedPhoneSearchAgent

def test_with_sample():
    """Test the agent with a small sample of companies"""
    
    # Load a small sample from the data
    input_file = 'infobelscrapping/datoscif_companies_final.json'
    
    print("Loading sample companies...")
    with open(input_file, 'r', encoding='utf-8') as f:
        all_companies = json.load(f)
    
    # Take first 3 companies for testing
    sample_companies = all_companies[:3]
    
    print(f"Testing with {len(sample_companies)} companies:")
    for i, company in enumerate(sample_companies):
        print(f"{i+1}. {company['company_name']} - {company['municipality']}, {company['province']}")
    
    # Initialize agent with faster delay for testing
    agent = EnhancedPhoneSearchAgent(search_delay=1.0)
    
    print("\nStarting phone number search...")
    results = agent.process_companies_batch(sample_companies, 0, len(sample_companies))
    
    # Show results
    print("\n" + "="*50)
    print("RESULTS:")
    print("="*50)
    
    phones_found = 0
    for result in results:
        company_name = result['company_name']
        phone = result.get('phone', 'Not found')
        search_info = result.get('phone_search_info', 'No info')
        
        if phone and phone != 'Not found':
            phones_found += 1
            print(f"✓ {company_name}")
            print(f"  Phone: {phone}")
        else:
            print(f"✗ {company_name}")
            print(f"  Status: {search_info}")
        print()
    
    print(f"Summary: Found {phones_found}/{len(results)} phone numbers")
    
    # Save test results
    with open('test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("Test results saved to 'test_results.json'")

def test_phone_extraction():
    """Test phone number extraction functionality"""
    agent = EnhancedPhoneSearchAgent()
    
    test_texts = [
        "Contacto: +34 912 345 678",
        "Teléfono: 934567890",
        "Llama al 91-234-56-78",
        "Phone: +34 666 777 888",
        "Tel: 987654321",
        "No phone number here",
        "Mixed text with 612345678 somewhere in middle"
    ]
    
    print("Testing phone number extraction:")
    print("="*40)
    
    for text in test_texts:
        phones = agent.extract_phones(text)
        print(f"Text: {text}")
        print(f"Found: {phones if phones else 'No phones found'}")
        print()

if __name__ == "__main__":
    print("Phone Search Agent Test")
    print("="*30)
    
    choice = input("\nChoose test:\n1. Test phone extraction\n2. Test with sample companies\nEnter choice (1 or 2): ")
    
    if choice == "1":
        test_phone_extraction()
    elif choice == "2":
        test_with_sample()
    else:
        print("Invalid choice. Running phone extraction test...")
        test_phone_extraction()