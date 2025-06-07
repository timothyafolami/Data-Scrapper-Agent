import scrapy
from infobelscrapping.items import DatoscifscrappingItem
import re


class DatoscifSpider(scrapy.Spider):
    name = 'datoscif'
    allowed_domains = ['datoscif.es']
    start_urls = ['https://www.datoscif.es/empresas-nuevas/empresas-creadas-hoy-en-espana/']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'ROBOTSTXT_OBEY': True,
        'COOKIES_ENABLED': True,
    }

    def parse(self, response):
        self.logger.info(f"Processing page: {response.url}")
        
        # Extract company blocks using the correct selector
        company_blocks = response.css('div.bloq-empr-nueva')
        self.logger.info(f"Found {len(company_blocks)} company blocks")
        
        for block in company_blocks:
            company_data = {}
            
            # Extract company name
            company_name = block.css('.nom-empr a::text').get()
            if company_name:
                company_data['company_name'] = company_name.strip()
                company_data['url'] = response.urljoin(block.css('.nom-empr a::attr(href)').get() or '')
            
            # Extract all data fields
            # Get all p elements with data
            data_rows = block.css('p')
            current_field = None
            
            for p in data_rows:
                text = p.css('::text').get()
                if text:
                    text = text.strip()
                    
                    # Check if this is a field label
                    if p.css('::attr(class)').get() == 'filaPr':
                        current_field = text.lower()
                    else:
                        # This is a value
                        if current_field == 'fecha inicio':
                            company_data['start_date'] = text
                        elif current_field == 'capital social':
                            company_data['social_capital'] = text
                        elif current_field == 'coordenadas':
                            company_data['coordinates'] = text
                        elif current_field == 'calle':
                            company_data['address'] = text
                        elif current_field == 'cp':
                            company_data['postal_code'] = text
                        elif current_field == 'municipio':
                            company_data['municipality'] = text
                        elif current_field == 'provincia':
                            company_data['province'] = text
                        elif current_field == 'objeto social':
                            company_data['business_purpose'] = text
            
            # Yield the item if we have a company name
            if company_data.get('company_name'):
                item = self.create_company_item(company_data, response.url)
                yield item
        
        # Handle pagination - follow all pagination links systematically
        current_page_num = self.extract_page_number(response.url)
        self.logger.info(f"Current page: {current_page_num}")
        
        # Find all pagination links on the page
        pagination_links = response.css('a[href*="empresas-creadas-hoy-en-espana"]')
        next_pages_found = []
        
        for link in pagination_links:
            href = link.css('::attr(href)').get()
            link_text = link.css('::text').get()
            
            if href and link_text:
                link_text = link_text.strip()
                
                # Extract page number from href
                target_page = self.extract_page_number(href)
                
                # Follow next sequential page (current + 1)
                if target_page == current_page_num + 1:
                    self.logger.info(f"Following next page {target_page}: {href}")
                    yield response.follow(href, self.parse)
                    break
                
                # Collect all higher page numbers for potential fallback
                elif target_page > current_page_num:
                    next_pages_found.append((target_page, href))
        
        # If no direct next page found, try the lowest available higher page
        if not any(target_page == current_page_num + 1 for target_page, href in next_pages_found):
            if next_pages_found:
                # Sort by page number and take the lowest
                next_pages_found.sort(key=lambda x: x[0])
                target_page, href = next_pages_found[0]
                self.logger.info(f"Following available page {target_page}: {href}")
                yield response.follow(href, self.parse)

    def parse_text_patterns(self, response):
        # Extract all text and try to find company patterns
        all_text = response.css('*::text').getall()
        text_lines = [line.strip() for line in all_text if line.strip()]
        
        current_company = {}
        for i, line in enumerate(text_lines):
            line_lower = line.lower()
            
            # Look for company names (usually appear before "Fecha inicio")
            if i < len(text_lines) - 1 and 'fecha inicio' in text_lines[i + 1].lower():
                current_company['company_name'] = line
                current_company['url'] = response.url
                continue
                
            # Parse specific fields
            if 'fecha inicio:' in line_lower:
                current_company['start_date'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif 'capital social:' in line_lower:
                current_company['social_capital'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif 'coordenadas:' in line_lower:
                current_company['coordinates'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif 'calle:' in line_lower:
                current_company['address'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif line_lower.startswith('cp:'):
                current_company['postal_code'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif 'municipio:' in line_lower:
                current_company['municipality'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif 'provincia:' in line_lower:
                current_company['province'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif 'objeto social:' in line_lower:
                current_company['business_purpose'] = line.split(':', 1)[1].strip() if ':' in line else ''
                
                # End of company data, yield item
                if current_company.get('company_name'):
                    yield self.create_company_item(current_company, response.url)
                    current_company = {}

    def parse_company_block(self, block, response):
        company_data = {}
        
        # Extract company name
        company_name = block.css('h3::text, a::text, .name::text').get()
        if company_name:
            company_data['company_name'] = company_name.strip()
            
        # Extract all text from the block and parse
        block_text = block.css('*::text').getall()
        for text in block_text:
            text = text.strip()
            if ':' in text:
                field, value = text.split(':', 1)
                field_lower = field.lower().strip()
                value = value.strip()
                
                if 'fecha inicio' in field_lower:
                    company_data['start_date'] = value
                elif 'capital social' in field_lower:
                    company_data['social_capital'] = value
                elif 'coordenadas' in field_lower:
                    company_data['coordinates'] = value
                elif 'calle' in field_lower:
                    company_data['address'] = value
                elif 'cp' in field_lower:
                    company_data['postal_code'] = value
                elif 'municipio' in field_lower:
                    company_data['municipality'] = value
                elif 'provincia' in field_lower:
                    company_data['province'] = value
                elif 'objeto social' in field_lower:
                    company_data['business_purpose'] = value
        
        if company_data.get('company_name'):
            company_data['url'] = response.url
            yield self.create_company_item(company_data, response.url)

    def extract_page_number(self, url):
        """Extract page number from URL"""
        import re
        
        # Look for page number at the end of the URL path
        # Pattern: /empresas-creadas-hoy-en-espana/2, /empresas-creadas-hoy-en-espana/3, etc.
        page_match = re.search(r'/empresas-creadas-hoy-en-espana/(\d+)', url)
        if page_match:
            return int(page_match.group(1))
        
        # Look for other page parameter patterns
        page_match = re.search(r'page[=/](\d+)', url)
        if page_match:
            return int(page_match.group(1))
        
        # If no page parameter, assume it's page 1
        return 1

    def create_company_item(self, company_data, source_url):
        item = DatoscifscrappingItem()
        item['company_name'] = company_data.get('company_name', '')
        item['start_date'] = company_data.get('start_date', '')
        item['social_capital'] = company_data.get('social_capital', '')
        item['coordinates'] = company_data.get('coordinates', '')
        item['address'] = company_data.get('address', '')
        item['postal_code'] = company_data.get('postal_code', '')
        item['municipality'] = company_data.get('municipality', '')
        item['province'] = company_data.get('province', '')
        item['business_purpose'] = company_data.get('business_purpose', '')
        item['url'] = company_data.get('url', source_url)
        return item