# Quick Start Guide for Enhanced Features

## 🚀 Installation & Setup

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install updated dependencies
pip install -r requirements.txt

# Download TextBlob corpora (required for sentiment analysis)
python -m textblob.download_corpora

# Verify installation
python -c "from textblob import TextBlob; print('TextBlob ready!')"
```

### 2. Frontend Setup

The frontend already has all required dependencies (recharts is included).

```bash
cd Move/frontend

# Verify recharts is installed
npm list recharts

# If needed, reinstall dependencies
npm install
```

### 3. Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd Move/frontend
npm run dev
```

---

## 🧪 Testing the New Features

### Test 1: Basic Enhanced Analysis
```bash
curl -X POST http://localhost:8000/explain \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "date": "2024-01-15",
    "include_historical": true,
    "include_sector_analysis": true,
    "include_sentiment": true,
    "days_range": 30
  }'
```

### Test 2: Historical Data Only
```bash
curl http://localhost:8000/historical/AAPL?end_date=2024-01-15&days=30
```

### Test 3: News Timeline
```bash
curl http://localhost:8000/news-timeline/AAPL?end_date=2024-01-15&days=7
```

### Test 4: Sector Context
```bash
curl http://localhost:8000/sector-context/AAPL?date=2024-01-15
```

### Test 5: Compare Multiple Stocks
```bash
curl "http://localhost:8000/compare?symbols=AAPL,MSFT,GOOGL&date=2024-01-15"
```

---

## 🎯 Using the Web Interface

### Navigate Through Tabs

1. **Search for a Stock**
   - Enter symbol (e.g., AAPL)
   - Select date
   - Click "Analyze"

2. **Overview Tab** (Default)
   - Primary driver
   - AI explanation
   - Confidence score
   - Supporting factors

3. **Charts & Indicators Tab**
   - Historical price chart with MA-20 and MA-50
   - News events overlaid on timeline
   - Volume chart
   - Interactive tooltips

4. **Sector Analysis Tab**
   - Market indices (S&P 500, NASDAQ)
   - Sector performance
   - Relative strength
   - Peer stock comparison
   - Correlation analysis

5. **News & Sentiment Tab**
   - Sentiment overview (positive/negative/neutral counts)
   - Click sentiment cards to filter
   - Adjust credibility slider
   - View sentiment timeline chart
   - Browse filtered news articles

6. **Multi-Day Trends Tab**
   - Pattern type (Uptrend, Downtrend, etc.)
   - Cumulative change visualization
   - Performance chart
   - Technical indicators (MA-20, MA-50, RSI, Volume)

---

## 📊 Understanding the Visualizations

### Price Chart
- **Blue line**: Closing price
- **Green dashed line**: 20-day moving average
- **Orange dashed line**: 50-day moving average
- **Red vertical line**: Target analysis date
- **Colored dots**: News events (green=positive, red=negative, gray=neutral)

### Volume Chart
- **Blue bars**: Daily trading volume
- **Height**: Relative volume (taller = higher volume)
- **Red line**: Target date marker

### Sector Comparison Chart
- **Bars**: Performance comparison
- **Colors**: Green (positive), Red (negative)
- **Highlighted bar**: Your selected stock (blue border)

### Sentiment Timeline
- **Area chart**: Average daily sentiment
- **Dots**: Each day with news coverage
- **Hover**: See articles for that day

### Cumulative Performance
- **Area fill**: Shows trend direction (green=up, red=down)
- **Line**: Cumulative change from start date
- **Dots**: Daily data points

---

## 🔧 Troubleshooting

### Issue: Sentiment Analysis Not Working
```bash
# Download TextBlob corpora
python -m textblob.download_corpora

# Or manually install
python -m nltk.downloader brown
python -m nltk.downloader punkt
```

### Issue: Charts Not Displaying
- Check browser console for errors
- Verify recharts is installed: `npm list recharts`
- Clear browser cache and reload

### Issue: Historical Data Missing
- Ensure date is a valid trading day (weekdays, not holidays)
- Yahoo Finance may not have data for very old dates
- Try a more recent date

### Issue: Sector Context Not Available
- Stock must be in the sector mapping (see `market_data.py`)
- Add your stock to `STOCK_SECTOR_MAP` if needed

### Issue: News Timeline Empty
- Verify NewsAPI key is valid in `.env`
- NewsAPI free tier has limitations (30 days historical)
- Try a more recent date

---

## 🎨 Customization Tips

### Adjust Chart Colors
Edit `PriceChart.tsx`:
```typescript
// Change price line color
stroke="#3b82f6"  // Default blue

// Change MA colors
stroke="#10b981"  // MA-20 green
stroke="#f59e0b"  // MA-50 orange
```

### Change Date Range
Edit `page.tsx` or use API parameters:
```typescript
// Default 30 days
days_range: 30

// Extend to 60 days
days_range: 60
```

### Modify Sentiment Thresholds
Edit `news_service.py`:
```python
# Adjust sentiment classification
if polarity > 0.1:  # More strict: > 0.2
    label = "positive"
```

### Add More Sectors
Edit `market_data.py`:
```python
STOCK_SECTOR_MAP = {
    "YOUR_SYMBOL": ("Sector Name", "ETF_SYMBOL"),
    # Example:
    "NFLX": ("Communication Services", "XLC"),
}
```

---

## 📈 Best Practices

### For Best Results:
1. **Use Recent Dates**: More reliable data and news coverage
2. **Popular Stocks**: Better sector/peer comparisons (AAPL, MSFT, etc.)
3. **Trading Days**: Use weekdays, avoid weekends/holidays
4. **Check All Tabs**: Each provides unique insights

### Performance Tips:
1. **Limit Date Range**: 30-60 days is optimal
2. **Don't Over-Filter**: Some news better than none
3. **Cache Results**: Save analyses you want to revisit

---

## 🆘 Support

If you encounter issues:

1. Check the console logs (browser F12)
2. Check backend logs (terminal running uvicorn)
3. Verify API keys are set in `.env`
4. Ensure all dependencies are installed
5. Try the test endpoints first

---

## ✨ Enjoy Your Enhanced Stock Analysis Tool!

You now have a comprehensive platform for:
- 📊 Analyzing stock movements
- 📈 Tracking historical trends
- 📰 Understanding news impact
- 🎯 Comparing sector performance
- 💡 Making informed decisions

Happy analyzing! 🚀
