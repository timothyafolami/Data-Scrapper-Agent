import json
import re
import time
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from urllib.parse import quote_plus
import os

@dataclass
class SearchResult:
    title: str
    snippet: str
    url: str
    phone_found: Optional[str] = None

class EnhancedPhoneSearchAgent:
    def __init__(self, search_delay: float = 1.0):
        self.search_delay = search_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Spanish phone number patterns
        self.phone_patterns = [
            r'(\+34[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{3})',  # +34 format
            r'(\+34[\s\-]?\d{2}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2})',  # +34 alternative
            r'(\d{3}[\s\-]?\d{3}[\s\-]?\d{3})',  # 9 digits with separators
            r'(\d{2}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2})',  # 8 digits + area code
            r'(\d{3}[\s\-]?\d{2}[\s\-]?\d{2}[\s\-]?\d{2})',  # Alternative format
            r'(9\d{8})',  # Mobile numbers starting with 9
            r'(8\d{8})',  # Some landlines starting with 8
            r'(6\d{8})',  # Mobile numbers starting with 6
            r'(7\d{8})',  # Mobile numbers starting with 7
        ]
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def clean_phone_number(self, phone: str) -> str:
        """Clean and standardize phone number format"""
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Add +34 if it's a Spanish number without country code
        if cleaned.startswith('34') and len(cleaned) == 11:
            cleaned = '+' + cleaned
        elif len(cleaned) == 9 and cleaned[0] in '6789':
            cleaned = '+34' + cleaned
            
        return cleaned
    
    def extract_phones(self, text: str) -> List[str]:
        """Extract all phone numbers from text"""
        phones = []
        
        for pattern in self.phone_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                cleaned = self.clean_phone_number(match)
                if len(cleaned.replace('+34', '')) >= 8:  # Minimum 8 digits
                    phones.append(cleaned)
        
        return list(set(phones))  # Remove duplicates
    
    def search_duckduckgo(self, query: str) -> List[SearchResult]:
        """Search using DuckDuckGo (free alternative to Google)"""
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                # Parse search results (simplified - you might want more robust parsing)
                results = []
                # This is a simplified parser - you'd want more robust HTML parsing
                text_content = response.text
                
                # Extract snippets that might contain phone numbers
                snippet_pattern = r'<a class="result__snippet"[^>]*>(.*?)</a>'
                snippets = re.findall(snippet_pattern, text_content, re.DOTALL)
                
                for snippet in snippets[:5]:  # Take first 5 results
                    # Clean HTML tags
                    clean_snippet = re.sub(r'<[^>]+>', '', snippet)
                    phones = self.extract_phones(clean_snippet)
                    
                    result = SearchResult(
                        title="DuckDuckGo Result",
                        snippet=clean_snippet[:200],
                        url="",
                        phone_found=phones[0] if phones else None
                    )
                    results.append(result)
                
                return results
        except Exception as e:
            self.logger.error(f"DuckDuckGo search error: {e}")
        
        return []
    
    def search_company_multiple_strategies(self, company_data: Dict) -> Tuple[Optional[str], str]:
        """Try multiple search strategies to find phone number"""
        company_name = company_data['company_name']
        municipality = company_data.get('municipality', '')
        province = company_data.get('province', '')
        
        search_queries = [
            f'"{company_name}" {municipality} teléfono contacto',
            f'"{company_name}" {municipality} {province} teléfono',
            f'{company_name} {municipality} contacto phone',
            f'"{company_name}" Spain contact phone',
            f'{company_name} {municipality} {province} empresa'
        ]
        
        for i, query in enumerate(search_queries):
            self.logger.info(f"Strategy {i+1}: {query}")
            
            results = self.search_duckduckgo(query)
            
            # Look for phone numbers in results
            for result in results:
                if result.phone_found:
                    return result.phone_found, f"Found via search strategy {i+1}"
            
            time.sleep(self.search_delay)
        
        return None, "No phone found after all strategies"
    
    def process_companies_batch(self, companies_data: List[Dict], start_idx: int = 0, batch_size: int = 50) -> List[Dict]:
        """Process companies in batches to handle large datasets"""
        results = []
        end_idx = min(start_idx + batch_size, len(companies_data))
        
        self.logger.info(f"Processing companies {start_idx} to {end_idx}")
        
        for i in range(start_idx, end_idx):
            company_data = companies_data[i]
            company_name = company_data['company_name']
            
            self.logger.info(f"Processing {i+1}/{len(companies_data)}: {company_name}")
            
            try:
                phone, search_info = self.search_company_multiple_strategies(company_data)
                
                # Update company data
                updated_company = company_data.copy()
                updated_company['phone'] = phone
                updated_company['phone_search_info'] = search_info
                updated_company['search_timestamp'] = time.time()
                
                results.append(updated_company)
                
                if phone:
                    self.logger.info(f"✓ Found phone for {company_name}: {phone}")
                else:
                    self.logger.info(f"✗ No phone found for {company_name}")
                    
            except Exception as e:
                self.logger.error(f"Error processing {company_name}: {e}")
                updated_company = company_data.copy()
                updated_company['phone'] = None
                updated_company['phone_search_info'] = f"Error: {str(e)}"
                results.append(updated_company)
        
        return results
    
    def save_progress(self, results: List[Dict], output_file: str, stats: Dict):
        """Save results and statistics"""
        # Save results
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save statistics
        stats_file = output_file.replace('.json', '_stats.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Progress saved to {output_file}")
        self.logger.info(f"Statistics saved to {stats_file}")

def main():
    input_file = 'infobelscrapping/datoscif_companies_final.json'
    output_file = 'companies_with_phones_enhanced.json'
    
    # Load data
    with open(input_file, 'r', encoding='utf-8') as f:
        companies_data = json.load(f)
    
    print(f"Loaded {len(companies_data)} companies")
    
    # Initialize agent
    agent = EnhancedPhoneSearchAgent(search_delay=2.0)  # 2 second delay between searches
    
    # Process in batches
    batch_size = 20  # Process 20 companies at a time
    all_results = []
    
    for start_idx in range(0, len(companies_data), batch_size):
        batch_results = agent.process_companies_batch(
            companies_data, start_idx, batch_size
        )
        all_results.extend(batch_results)
        
        # Calculate statistics
        phones_found = sum(1 for r in all_results if r.get('phone'))
        stats = {
            'total_processed': len(all_results),
            'phones_found': phones_found,
            'success_rate': phones_found / len(all_results) if all_results else 0,
            'last_processed_batch': f"{start_idx}-{start_idx + len(batch_results)}"
        }
        
        # Save progress after each batch
        agent.save_progress(all_results, output_file, stats)
        
        print(f"Batch completed. Found {phones_found}/{len(all_results)} phone numbers so far")
        
        # Brief pause between batches
        time.sleep(5)
    
    print(f"Final results: Found {stats['phones_found']}/{stats['total_processed']} phone numbers")
    print(f"Success rate: {stats['success_rate']:.2%}")

if __name__ == "__main__":
    main()