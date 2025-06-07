import requests
import time
from bs4 import BeautifulSoup

def test_direct_access():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    # First, try to access the home page
    print("Testing direct access...")
    
    try:
        # Start with home page
        resp = session.get('https://www.infobel.com', timeout=10)
        print(f"Home page status: {resp.status_code}")
        
        time.sleep(3)
        
        # Then try the category page
        url = 'https://www.infobel.com/es/spain/business/10000/alimentacion_hosteleria'
        resp = session.get(url, timeout=10)
        print(f"Category page status: {resp.status_code}")
        print(f"Final URL: {resp.url}")
        
        if 'Abuse' in resp.url:
            print("Redirected to abuse page - anti-bot protection detected")
            return False
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        title = soup.find('title')
        print(f"Page title: {title.text if title else 'No title'}")
        
        # Look for business listings
        business_links = soup.find_all('a', href=lambda x: x and 'business' in x)
        print(f"Business links found: {len(business_links)}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_direct_access()