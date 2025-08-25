# 📊 InfluenceTracker

**AI-Powered YouTube Trend Analysis for Brand Teams**

Track selected YouTube channels, summarize new videos with AI, and generate a 48-hour trend brief with a shareable Streamlit app.

## 🎯 What It Does

- **Monitor YouTube Channels**: Input channel IDs and fetch latest videos
- **AI-Powered Analysis**: Generate summaries, sentiment analysis, and trend extraction
- **Trend Briefs**: Aggregate insights into executive summaries
- **Data Export**: Download results as CSV for further analysis
- **Smart Caching**: Avoid duplicate processing with local JSON storage

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- YouTube Data API v3 key
- Google Gemini API key (OpenAI optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd influence-tracker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.sample .env
   # Edit .env with your API keys
   ```

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

## 🔑 API Keys Setup

### YouTube Data API v3
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Add to `.env` as `YOUTUBE_API_KEY`

### Google Gemini
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to `.env` as `GEMINI_API_KEY`

### OpenAI (Optional Fallback)
1. Get API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Add to `.env` as `OPENAI_API_KEY`

## 📖 Usage

### 1. Input Channel IDs
Enter YouTube channel IDs in UC... format (one per line):
```
UC_x5XG1OV2P6uZZ5FSM9Ttw  # Google Developers
UCBJycsmduvYEL83R_U4JriQ  # MKBHD
```

### 2. Configure Settings
- **Videos per channel**: 1-5 videos to analyze
- **Rate limit delay**: 2-30 seconds between AI calls
- **Business niche**: Context for AI analysis
- **AI Model**: Gemini (default) or OpenAI

### 3. Fetch & Analyze
Click "Fetch + Summarize" to:
- Fetch latest videos from channels
- Generate AI summaries with sentiment
- Extract trending topics
- Cache results locally

### 4. Generate Brief
Click "Generate Brief" to create:
- Top 5 trends with counts
- Sentiment distribution
- Executive summary with insights

### 5. Export Data
Download results as CSV for:
- Further analysis in Excel/Google Sheets
- Integration with other tools
- Reporting and presentations

## 🏗️ Architecture

```
app.py                 # Main Streamlit application
├── services/
│   ├── youtube_fetch.py    # YouTube API integration
│   ├── ai_summarize.py     # AI summarization (Gemini/OpenAI)
│   ├── cache_store.py      # Local JSON caching
│   └── brief.py            # Trend analysis & brief generation
├── data/                   # Runtime data storage (gitignored)
└── requirements.txt        # Python dependencies
```

## 🎨 Features

### Core Functionality
- ✅ YouTube channel monitoring
- ✅ AI-powered content summarization
- ✅ Sentiment analysis (positive/neutral/negative)
- ✅ Trend extraction and aggregation
- ✅ Executive brief generation
- ✅ CSV export
- ✅ Local caching with deduplication

### Advanced Features
- 🔄 OpenAI fallback if Gemini fails
- ⏱️ Configurable rate limiting
- 📊 Interactive Plotly charts
- 🎯 Business niche context
- 🗄️ Smart cache management
- 📱 Responsive Streamlit UI

## 🚀 Deployment

### Streamlit Cloud
1. Push code to GitHub
2. Connect repository to [Streamlit Cloud](https://streamlit.io/cloud)
3. Set secrets in Streamlit Cloud dashboard:
   - `YOUTUBE_API_KEY`
   - `GEMINI_API_KEY`
   - `OPENAI_API_KEY` (optional)
4. Deploy!

### Local Development
```bash
streamlit run app.py --server.port 8501
```

## 🧪 Demo Script

### Test with Sample Channels
1. **Google Developers**: `UC_x5XG1OV2P6uZZ5FSM9Ttw`
2. **MKBHD**: `UCBJycsmduvYEL83R_U4JriQ`
3. **Verge**: `UCddiUEpeqJcYeBxX1IVBKvQ`

### Demo Flow
1. Enter channel IDs (one per line)
2. Set niche: "Technology & Innovation"
3. Videos per channel: 3
4. Rate limit: 5 seconds
5. Click "Fetch + Summarize"
6. Wait for processing (1-2 minutes)
7. Review results and charts
8. Generate executive brief
9. Export CSV

## 🔧 Troubleshooting

### Common Issues

**YouTube API Quota Exceeded**
- Reduce videos per channel
- Increase rate limit delay
- Check API quota in Google Cloud Console

**Gemini API Errors**
- Verify API key is correct
- Check Gemini API status
- Try OpenAI fallback if available

**Rate Limiting (429 errors)**
- Increase delay between calls
- Use slider to set higher values (10-30 seconds)

**Channel ID Validation**
- Ensure format: UC + 22 characters
- Example: `UC_x5XG1OV2P6uZZ5FSM9Ttw`

### Performance Tips
- Start with 1-2 channels for testing
- Use 5-10 second delays for production
- Monitor API quotas regularly
- Clear cache if needed

## 📊 Data Model

### Post Structure
```json
{
  "platform": "YouTube",
  "channel_id": "UC...",
  "post_id": "VIDEO_ID",
  "title": "Video Title",
  "url": "https://youtube.com/watch?v=...",
  "published_at": "2024-01-01T00:00:00Z",
  "summary": "AI-generated summary...",
  "sentiment": "positive|neutral|negative",
  "trends": "trend1,trend2,trend3",
  "cached_at": "2024-01-01T00:00:00Z"
}
```

### Cache Structure
```json
{
  "posts": [...],
  "meta": {
    "last_run": "ISO timestamp",
    "total_posts": 42,
    "last_updated": "ISO timestamp"
  }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: Create GitHub issue
- **Documentation**: Check this README
- **API Limits**: Monitor Google Cloud Console

---

**Built with ❤️ for hackathons and brand teams**
