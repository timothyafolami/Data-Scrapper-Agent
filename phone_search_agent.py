import json
import re
import time
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

@dataclass
class Company:
    company_name: str
    address: str
    municipality: str
    province: str
    postal_code: str
    phone: Optional[str] = None
    search_status: str = "pending"
    
class PhoneSearchAgent:
    def __init__(self, search_delay: float = 1.0):
        self.search_delay = search_delay
        self.phone_patterns = [
            r'(\+34\s?\d{3}\s?\d{3}\s?\d{3})',
            r'(\d{3}[\s\-]?\d{3}[\s\-]?\d{3})',
            r'(\d{2}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2})',
            r'(\d{3}[\s\-]?\d{2}[\s\-]?\d{2}[\s\-]?\d{2})',
        ]
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text using regex patterns"""
        for pattern in self.phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                phone = matches[0].strip()
                # Clean up the phone number
                phone = re.sub(r'[\s\-]', '', phone)
                if len(phone) >= 9:
                    return phone
        return None
    
    def search_company_phone(self, company: Company) -> Optional[str]:
        """Search for company phone number using web search"""
        search_query = f'"{company.company_name}" {company.municipality} {company.province} teléfono contacto'
        
        try:
            # Using requests to simulate web search (you might want to integrate with actual search APIs)
            self.logger.info(f"Searching for: {search_query}")
            
            # Here you would integrate with actual search API like Google Custom Search API
            # For now, this is a placeholder that shows the structure
            
            # Alternative approach: try searching company websites directly
            website_search_query = f'"{company.company_name}" {company.municipality} site:*.es teléfono'
            
            # Placeholder for actual search implementation
            # You'll need to integrate with search APIs or scraping services
            
            time.sleep(self.search_delay)
            return None
            
        except Exception as e:
            self.logger.error(f"Error searching for {company.company_name}: {e}")
            return None
    
    def process_companies(self, companies_data: List[Dict]) -> List[Dict]:
        """Process all companies to find phone numbers"""
        results = []
        
        for i, company_data in enumerate(companies_data):
            company = Company(
                company_name=company_data['company_name'],
                address=company_data.get('address', ''),
                municipality=company_data.get('municipality', ''),
                province=company_data.get('province', ''),
                postal_code=company_data.get('postal_code', '')
            )
            
            self.logger.info(f"Processing {i+1}/{len(companies_data)}: {company.company_name}")
            
            phone = self.search_company_phone(company)
            
            # Update company data with phone number
            updated_company = company_data.copy()
            updated_company['phone'] = phone
            updated_company['search_status'] = 'completed' if phone else 'no_phone_found'
            
            results.append(updated_company)
            
            # Progress logging
            if (i + 1) % 10 == 0:
                self.logger.info(f"Processed {i+1} companies")
        
        return results
    
    def save_results(self, results: List[Dict], output_file: str):
        """Save results to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Results saved to {output_file}")

def main():
    # Load company data
    input_file = 'infobelscrapping/datoscif_companies_final.json'
    output_file = 'companies_with_phones.json'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        companies_data = json.load(f)
    
    # Initialize agent
    agent = PhoneSearchAgent(search_delay=1.0)
    
    # Process companies (you might want to process in batches)
    print(f"Processing {len(companies_data)} companies...")
    results = agent.process_companies(companies_data)
    
    # Save results
    agent.save_results(results, output_file)
    
    # Statistics
    found_phones = sum(1 for r in results if r.get('phone'))
    print(f"Found phone numbers for {found_phones}/{len(results)} companies")

if __name__ == "__main__":
    main()