# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import re
import json
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class DataCleaningPipeline:
    """Clean and validate scraped data"""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Clean company name
        if adapter.get('company_name'):
            adapter['company_name'] = adapter['company_name'].strip()
        else:
            raise DropItem(f"Missing company name: {item}")
        
        # For datoscif spider, we don't have phone data - skip phone validation
        # Keep for backwards compatibility with other spiders
        if adapter.get('phone'):
            phone = adapter['phone']
            # Remove extra whitespace and normalize
            phone = re.sub(r'\s+', ' ', phone.strip())
            # Validate Spanish phone format
            if re.search(r'(\+34\s?\d{9}|\d{9})', phone):
                adapter['phone'] = phone
            else:
                adapter['phone'] = 'Invalid format'
        
        # Clean address
        if adapter.get('address'):
            address = adapter['address']
            # Remove extra whitespace
            address = re.sub(r'\s+', ' ', address.strip())
            adapter['address'] = address
        else:
            adapter['address'] = 'Not available'
        
        # Validate URL/link
        if adapter.get('url'):
            url = adapter['url'].strip()
            if url and not url.startswith('http'):
                adapter['url'] = f"https://www.datoscif.es{url}"
        elif adapter.get('link'):
            link = adapter['link'].strip()
            if not link.startswith('http'):
                adapter['link'] = f"https://www.infobel.com{link}"
        else:
            if not adapter.get('url'):
                adapter['url'] = 'Not available'
        
        # Only set category for old-style items (backwards compatibility)
        if 'category' in adapter.keys() and not adapter.get('category'):
            adapter['category'] = 'alimentacion_hosteleria'
        
        return item


class DuplicatesPipeline:
    """Remove duplicate companies based on name and link"""
    
    def __init__(self):
        self.seen_items = set()
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Create unique identifier - handle both old and new field names
        company_name = adapter.get('company_name') or adapter.get('name', '')
        url = adapter.get('url') or adapter.get('link', '')
        identifier = (company_name.lower(), url)
        
        if identifier in self.seen_items:
            raise DropItem(f"Duplicate item: {company_name}")
        else:
            self.seen_items.add(identifier)
            return item


class StatsPipeline:
    """Collect statistics about scraped data"""
    
    def __init__(self):
        self.stats = {
            'total_items': 0,
            'items_with_phone': 0,
            'items_with_address': 0,
            'categories': {}
        }
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        self.stats['total_items'] += 1
        
        if adapter.get('phone') and adapter['phone'] not in ['Not available', 'Invalid format']:
            self.stats['items_with_phone'] += 1
        
        if adapter.get('address') and adapter['address'] != 'Not available':
            self.stats['items_with_address'] += 1
        
        category = adapter.get('category', 'unknown')
        self.stats['categories'][category] = self.stats['categories'].get(category, 0) + 1
        
        return item
    
    def close_spider(self, spider):
        # Save stats to file
        with open('scraping_stats.json', 'w') as f:
            json.dump(self.stats, f, indent=2)
        
        spider.logger.info(f"Scraping completed. Stats: {self.stats}")


class InfobelscrappingPipeline:
    """Main pipeline - placeholder for future enhancements"""
    
    def process_item(self, item, spider):
        return item
