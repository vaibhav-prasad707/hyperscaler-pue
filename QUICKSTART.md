# Quick Start Guide

## ✅ Setup Complete!

All dependencies are installed. Here's how to run the project:

## 1. Activate Virtual Environment

```bash
cd /Users/vaibhavprasad/Desktop/Projects/DataCentreSolution/hyperscaler-pue-benchmark
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

## 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
- Supabase URL and keys (get from https://supabase.com)
- Optional: Google CSE API key for enhanced searching

## 3. Set Up Supabase Database

1. Create a free project at https://supabase.com
2. Go to SQL Editor
3. Copy and paste the contents of `pipeline/schema.sql`
4. Run the query to create tables

## 4. Run Data Collection (Optional - for testing)

```bash
# Test with one scraper first
python scrapers/global_scraper.py

# Run all scrapers
python scrapers/indian_scraper.py
python scrapers/global_colocation_scraper.py
```

Note: These will attempt to download PDFs and scrape websites. Some may fail due to website changes or rate limiting.

## 5. Run Data Cleaner

```bash
python cleaner.py
```

This consolidates all JSON files into `data/processed/pue_benchmark.csv`

## 6. Load to Supabase

```bash
python pipeline/ingest.py
```

## 7. Run dbt Transformations

```bash
cd dbt_pue

# Configure dbt profile
cp profiles.yml.example ~/.dbt/profiles.yml
# Edit ~/.dbt/profiles.yml with your Supabase credentials

# Run dbt
dbt seed  # Load city temperatures
dbt run   # Build all models
dbt test  # Run quality tests

cd ..
```

## 8. Launch Dashboard

```bash
streamlit run dashboard/app.py
```

Dashboard opens at http://localhost:8501

## 🧪 Run Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_regex.py -v

# With coverage
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html
```

## 📝 Project Status

- ✅ Virtual environment created
- ✅ All dependencies installed (27 packages)
- ✅ Project structure complete
- ⏳ Environment variables needed
- ⏳ Supabase database setup needed

## 🎯 Next Steps

1. **Set up Supabase**: Get credentials and run schema.sql
2. **Configure .env**: Add your API keys
3. **Test scrapers**: Run one scraper to verify setup
4. **Build dashboard**: Run streamlit to see the UI

## 🔍 Troubleshooting

### Import Errors
Make sure virtual environment is activated:
```bash
source venv/bin/activate
```

### Supabase Connection Errors
- Verify credentials in `.env`
- Check project is not paused in Supabase dashboard
- Ensure firewall allows connections

### Scraper Failures
- Normal - some websites may block scraping
- Use known facilities data as fallback
- Check `data/collection_log.txt` for details

## 📚 Documentation

- **README.md** - Complete project documentation
- **powerbi/README.md** - Power BI setup guide
- **pipeline/schema.sql** - Database schema with comments

## 💡 Tips

- Start with the dashboard using sample data if scrapers fail
- The project is designed to work with partial data
- Check logs in `data/collection_log.txt` for debugging
- Each module can run independently for testing

---

**Ready to start!** Run the scrapers or jump straight to the dashboard with sample data.
