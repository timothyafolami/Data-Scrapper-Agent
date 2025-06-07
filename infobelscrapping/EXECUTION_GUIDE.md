# Quick Execution Guide - DatosCif Scraper

## 🚀 Getting Started

### 1. Test the Pipeline (Always run this first)
```bash
cd infobelscrapping
scrapy crawl test_pipeline -o test_output.json -L INFO
```

**✅ Expected Result:**
- 3 companies processed (1 duplicate removed)
- Files created: `test_output.json`, `scraping_stats.json`

### 2. Production Data Collection

#### Main Scraping Command
```bash
# Scrape all companies from DatosCif
scrapy crawl datoscif -o companies.json
```

#### Limited Testing
```bash
# Test with first 5 pages only
scrapy crawl datoscif -s CLOSESPIDER_PAGECOUNT=5 -o limited_companies.json
```

## 📊 Pipeline Processing

### Data Flow
```
Raw Data → DataCleaningPipeline → DuplicatesPipeline → StatsPipeline → Clean Output
```

### Generated Files
- `{output_name}.json` - Clean company data
- `scraping_stats.json` - Quality metrics

## 🔧 Commands Reference

### Main Commands
```bash
# Full scraping (all pages)
scrapy crawl datoscif -o companies.json

# Limited scraping (test)
scrapy crawl datoscif -s CLOSESPIDER_PAGECOUNT=5 -o test_companies.json

# Test pipeline functionality
scrapy crawl test_pipeline -o test_output.json -L INFO
```

### Output Formats
```bash
# JSON output (default)
scrapy crawl datoscif -o companies.json

# CSV output
scrapy crawl datoscif -o companies.csv

# JSON Lines output
scrapy crawl datoscif -o companies.jl
```

### Debug and Monitoring
```bash
# Debug mode (detailed logs)
scrapy crawl datoscif -L DEBUG

# Info level logging
scrapy crawl datoscif -L INFO

# Quiet mode (minimal output)
scrapy crawl datoscif -L WARNING
```

## 📈 Data Quality Metrics

After each run, check `scraping_stats.json`:
- **Total items**: Companies processed
- **Items with address**: Complete addresses
- **Duplicates dropped**: Removed redundancies

## 📍 Target Website

**Source**: https://www.datoscif.es/empresas-nuevas/empresas-creadas-hoy-en-espana/

**Data collected per company:**
- ✅ **Company Name**: Official business name
- ✅ **Start Date**: Registration date
- ✅ **Social Capital**: Initial capital amount
- ✅ **Coordinates**: Latitude/longitude
- ✅ **Address**: Complete street address
- ✅ **Postal Code**: ZIP code
- ✅ **Municipality**: City
- ✅ **Province**: State/province
- ✅ **Business Purpose**: CNAE codes and activities
- ✅ **URL**: Link to company profile

## ⚠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| No items extracted | Check if website structure changed |
| Connection errors | Verify internet connection |
| Blocked requests | Increase `DOWNLOAD_DELAY` in settings |
| Pipeline errors | Check field names match item definition |

## 🎯 Recommended Workflow

1. **Test**: `scrapy crawl test_pipeline -o test.json -L INFO`
2. **Limited Run**: `scrapy crawl datoscif -s CLOSESPIDER_PAGECOUNT=2 -o sample.json`
3. **Full Scrape**: `scrapy crawl datoscif -o all_companies.json`
4. **Validate**: Check `scraping_stats.json` for quality metrics

## 🚦 Performance Settings

**Current settings (optimized for respectful scraping):**
- Download delay: 2 seconds
- Concurrent requests: 1
- Respects robots.txt: Yes
- Random delay variation: Yes

## 📊 Expected Output Sample

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