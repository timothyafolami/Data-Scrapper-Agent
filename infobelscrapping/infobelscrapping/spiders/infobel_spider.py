import scrapy
from infobelscrapping.items import DatoscifscrappingItem
import re


class InfobelSpider(scrapy.Spider):
    name = 'infobel'
    allowed_domains = ['infobel.com']
    
    def start_requests(self):
        # Try starting with the home page first
        yield scrapy.Request(
            url='https://www.infobel.com',
            callback=self.parse_home,
            headers={
                'Referer': 'https://www.google.com/'
            }
        )
    
    def parse_home(self, response):
        # Wait a bit then go to the category page
        yield scrapy.Request(
            url='https://www.infobel.com/es/spain/business/10000/alimentacion_hosteleria',
            callback=self.parse,
            headers={
                'Referer': response.url
            },
            dont_filter=True
        )
    
    custom_settings = {
        'DOWNLOAD_DELAY': 8,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'ROBOTSTXT_OBEY': False,
        'COOKIES_ENABLED': True,
    }

    def parse(self, response):
        # Check if we got redirected to abuse page
        if 'Abuse' in response.url:
            self.logger.error("Got redirected to abuse page - anti-bot protection detected")
            return
        
        self.logger.info(f"Processing page: {response.url}")
        self.logger.info(f"Page title: {response.css('title::text').get()}")
        
        # Extract category from URL
        category = 'alimentacion_hosteleria'  # Default for this spider
        
        # Look for different types of company listings
        company_containers = []
        
        # Try various selectors for company listings
        selectors_to_try = [
            'div.listing-item',
            'div[class*="company"]',
            'div[class*="business"]', 
            'div[class*="result"]',
            'div[id*="listing"]',
            '.search-result',
            'tr[class*="result"]'
        ]
        
        for selector in selectors_to_try:
            containers = response.css(selector)
            if containers:
                company_containers = containers
                self.logger.info(f"Found {len(containers)} companies using selector: {selector}")
                break
        
        if not company_containers:
            # Fallback: look for any links that might be companies
            all_links = response.css('a')
            self.logger.info(f"No company containers found. Total links on page: {len(all_links)}")
            
            # Look for business-related links
            business_links = response.css('a[href*="/business/"], a[href*="/company/"], a[href*="/empresas/"]')
            self.logger.info(f"Found {len(business_links)} potential business links")
            
            for link in business_links[:5]:  # Limit to first 5 for testing
                name = link.css('::text').get()
                href = link.css('::attr(href)').get()
                
                if name and name.strip() and href:
                    item = DatoscifscrappingItem()
                    item['name'] = name.strip()
                    item['category'] = category
                    item['address'] = 'Address to be extracted'
                    item['phone'] = 'Phone to be extracted'
                    item['link'] = response.urljoin(href)
                    
                    # Follow the link to get details
                    yield response.follow(href, self.parse_company_detail, meta={'item': item})
        else:
            # Process company containers
            for container in company_containers:
                item = DatoscifscrappingItem()
                
                # Extract name
                name_selectors = ['h3 a::text', 'h2 a::text', 'a.title::text', '.name::text', 'a::text']
                name = None
                for name_sel in name_selectors:
                    name = container.css(name_sel).get()
                    if name:
                        break
                
                if name:
                    item['name'] = name.strip()
                    item['category'] = category
                    
                    # Extract address from container
                    address_text = ' '.join(container.css('::text').getall())
                    item['address'] = ' '.join(address_text.split())
                    
                    # Extract phone if available
                    phone = container.css('*[class*="phone"]::text, *[class*="tel"]::text').get()
                    item['phone'] = phone.strip() if phone else 'Not available'
                    
                    # Get link
                    link_elem = container.css('a::attr(href)').get()
                    item['link'] = response.urljoin(link_elem) if link_elem else response.url
                    
                    yield item
        
        # Look for pagination
        next_page_selectors = [
            'a[rel="next"]::attr(href)',
            'a.next::attr(href)',
            'a[class*="next"]::attr(href)',
            'a[href*="page"]:contains("Next")::attr(href)',
            'a[href*="alimentacion_hosteleria"]:contains("›")::attr(href)'
        ]
        
        for selector in next_page_selectors:
            next_page = response.css(selector).get()
            if next_page:
                yield response.follow(next_page, self.parse)
    
    def parse_company_detail(self, response):
        item = response.meta['item']
        
        # Extract address - try multiple selectors
        address = None
        
        # Try different address selectors
        address_selectors = [
            'span[itemprop="streetAddress"]::text',
            'div[class*="address"]::text',
            'span[class*="address"]::text',
            'div[class*="location"]::text',
            'div[class*="addr"]::text'
        ]
        
        for selector in address_selectors:
            address_parts = response.css(selector).getall()
            if address_parts:
                address = ' '.join([part.strip() for part in address_parts if part.strip()])
                break
        
        if not address:
            # Fallback: look for text near location icons
            location_text = response.xpath('//img[contains(@src, "location")]/following-sibling::text()').getall()
            if location_text:
                address = ' '.join([text.strip() for text in location_text if text.strip()])
        
        item['address'] = address or 'No address found'
        
        # Extract phone - try multiple approaches
        phone = None
        
        # Try different phone selectors
        phone_selectors = [
            'span[itemprop="telephone"]::text',
            'div[class*="phone"]::text',
            'span[class*="phone"]::text',
            'div[class*="tel"]::text',
            'a[href^="tel:"]::text'
        ]
        
        for selector in phone_selectors:
            phone_elem = response.css(selector).get()
            if phone_elem:
                phone = phone_elem.strip()
                break
        
        # Try to find phone in JavaScript or onclick handlers
        if not phone:
            phone_scripts = response.css('script::text').getall()
            for script in phone_scripts:
                if 'phone' in script.lower() or 'tel' in script.lower():
                    # Extract phone patterns
                    phone_patterns = re.findall(r'(\+34\s?\d{9}|\d{9})', script)
                    if phone_patterns:
                        phone = phone_patterns[0]
                        break
        
        # Try onclick handlers for encrypted phones
        if not phone:
            onclick_elements = response.css('[onclick*="phone"], [onclick*="displayPhone"]')
            if onclick_elements:
                phone = 'Phone available (encrypted)'
        
        item['phone'] = phone or 'No phone found'
        item['link'] = response.url
        
        yield item