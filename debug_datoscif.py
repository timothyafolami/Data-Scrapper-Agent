#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import re

def debug_datoscif():
    url = "https://www.datoscif.es/empresas-nuevas/empresas-creadas-hoy-en-espana/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print(f"Status: {response.status_code}")
    print(f"Content length: {len(response.text)}")
    
    # Look for patterns in the text
    text = soup.get_text()
    
    print("\n=== Looking for company-related keywords ===")
    keywords = ['Fecha inicio', 'Capital Social', 'Coordenadas', 'empresa', 'SL', 'SA']
    for keyword in keywords:
        count = text.count(keyword)
        print(f"{keyword}: {count} occurrences")
    
    print("\n=== Sample text content ===")
    lines = text.split('\n')
    for i, line in enumerate(lines[:50]):
        line = line.strip()
        if line and len(line) > 5:
            print(f"{i}: {line[:100]}")
    
    print("\n=== Looking for specific structures ===")
    # Look for table structures
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables")
    
    # Look for list structures
    uls = soup.find_all('ul')
    ols = soup.find_all('ol')
    print(f"Found {len(uls)} ul lists, {len(ols)} ol lists")
    
    # Look for divs with company-like content
    divs = soup.find_all('div')
    company_divs = []
    for div in divs:
        div_text = div.get_text()
        if 'Fecha inicio' in div_text or 'Capital Social' in div_text:
            company_divs.append(div)
    
    print(f"Found {len(company_divs)} divs with company data")
    
    if company_divs:
        print("\n=== Sample company div ===")
        sample_div = company_divs[0]
        print(sample_div.get_text()[:500])
        print(f"HTML: {str(sample_div)[:500]}")

if __name__ == "__main__":
    debug_datoscif()