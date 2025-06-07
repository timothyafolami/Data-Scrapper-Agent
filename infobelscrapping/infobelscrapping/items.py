# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DatoscifscrappingItem(scrapy.Item):
    company_name = scrapy.Field()
    start_date = scrapy.Field()
    social_capital = scrapy.Field()
    coordinates = scrapy.Field()
    address = scrapy.Field()
    postal_code = scrapy.Field()
    municipality = scrapy.Field()
    province = scrapy.Field()
    business_purpose = scrapy.Field()
    url = scrapy.Field()
