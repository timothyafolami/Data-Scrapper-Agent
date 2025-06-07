# DatosCif Company Scraper

A Scrapy-based web scraper for extracting newly created Spanish company data from DatosCif (datoscif.es).

## Features

- Extracts comprehensive company information from DatosCif
- Handles pagination automatically
- Includes data cleaning and validation pipelines
- Removes duplicate entries
- Generates detailed scraping statistics
- Robust error handling and retry mechanisms

## Project Structure

```
infobelscrapping/
├── scrapy.cfg                 # Scrapy configuration
├── infobelscrapping/
│   ├── __init__.py
│   ├── items.py              # Data item definitions
│   ├── middlewares.py        # Custom middlewares
│   ├── pipelines.py          # Data processing pipelines
│   ├── settings.py           # Scrapy settings
│   └── spiders/
│       ├── __init__.py
│       ├── datoscif_spider.py # Main spider for DatosCif
│       └── test_pipeline.py  # Pipeline testing spider
└── README.md
```

## Installation

1. Install required dependencies:
```bash
pip install scrapy beautifulsoup4 requests
```

2. Clone or download this project

## Usage

### Basic Scraping

Run the main spider to scrape company data:

```bash
cd infobelscrapping
scrapy crawl datoscif -o companies.json
```

### Test Pipeline

Test the data processing pipeline:

```bash
scrapy crawl test_pipeline -o test_output.json -L INFO
```

### Advanced Options

Limit the number of pages:
```bash
scrapy crawl datoscif -s CLOSESPIDER_PAGECOUNT=5 -o limited_companies.json
```

Set custom output format:
```bash
scrapy crawl datoscif -o companies.csv
scrapy crawl datoscif -o companies.jl  # JSON Lines
```

Control verbosity:
```bash
scrapy crawl datoscif -L INFO   # Show INFO level logs
scrapy crawl datoscif -L DEBUG  # Show DEBUG level logs
```

## Configuration

### Spider Settings

The spider includes several configurable settings in `spiders/datoscif_spider.py`:

- `DOWNLOAD_DELAY`: Delay between requests (default: 2 seconds)
- `RANDOMIZE_DOWNLOAD_DELAY`: Randomize delays (default: True)
- `CONCURRENT_REQUESTS`: Number of concurrent requests (default: 1)
- `ROBOTSTXT_OBEY`: Respect robots.txt (default: True)

### Global Settings

Modify `settings.py` to change global behavior:

- `USER_AGENT`: Browser user agent string
- `DEFAULT_REQUEST_HEADERS`: HTTP headers sent with requests
- `ITEM_PIPELINES`: Data processing pipeline configuration

## Data Fields

The scraper extracts the following information for each company:

- **Company Name**: Official company name
- **Start Date**: Company registration date
- **Social Capital**: Initial capital amount
- **Coordinates**: Geographic coordinates (latitude, longitude)
- **Address**: Complete street address
- **Postal Code**: Postal/ZIP code
- **Municipality**: City/municipality
- **Province**: Province/state
- **Business Purpose**: Company activities and CNAE codes
- **URL**: Link to company profile on DatosCif

## Pipelines

### DataCleaningPipeline
- Cleans and validates extracted data
- Normalizes addresses and company names
- Handles missing data gracefully
- Validates URLs

### DuplicatesPipeline
- Removes duplicate companies based on name and URL
- Maintains data integrity

### StatsPipeline
- Collects scraping statistics
- Tracks success rates
- Generates summary reports

## Output Formats

Supported output formats:
- JSON (`.json`)
- JSON Lines (`.jl`)
- CSV (`.csv`)
- XML (`.xml`)

## Target Website

This scraper targets: https://www.datoscif.es/empresas-nuevas/empresas-creadas-hoy-en-espana/

The site provides information about newly created companies in Spain, including:
- Daily updates of new company registrations
- Complete company registration details
- Geographic information
- Business activity classifications

## Error Handling

The scraper includes robust error handling:

- Automatic retries for failed requests
- Graceful handling of missing data
- Comprehensive logging
- Proper pagination handling

## Performance

Optimized for respectful scraping:
- Configurable delays between requests
- Randomized request timing
- Single concurrent request to avoid overloading servers
- Proper HTTP headers to appear as legitimate browser traffic
- Respects robots.txt

## Legal Considerations

- Always check and respect the website's robots.txt
- Be mindful of terms of service
- Use appropriate delays to avoid overloading servers
- Consider reaching out to data providers for official APIs

## Troubleshooting

### Common Issues

1. **Getting blocked**: Increase `DOWNLOAD_DELAY` in spider settings
2. **No data extracted**: Check if website structure has changed
3. **Connection errors**: Verify internet connection and target website availability

### Debug Mode

Run with debug logging to troubleshoot issues:
```bash
scrapy crawl datoscif -L DEBUG
```

### Testing

Use the test spider to verify pipeline functionality:
```bash
scrapy crawl test_pipeline -o test_output.json -L INFO
```

## Example Output

```json
{
  "company_name": "TECH SOLUTIONS BARCELONA SL",
  "start_date": "01/06/2025",
  "social_capital": "3.000,00 Euros",
  "coordinates": "41.40139535552083,2.197441270878622",
  "address": "Calle Gran Vía 25",
  "postal_code": "08013",
  "municipality": "Barcelona",
  "province": "Barcelona",
  "business_purpose": "Otras actividades de consultoría de gestión empresarial",
  "url": "https://www.datoscif.es/empresa/tech-solutions-barcelona-sl"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational purposes. Please ensure compliance with applicable laws and website terms of service.