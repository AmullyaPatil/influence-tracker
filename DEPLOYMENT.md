# Deployment Guide for InfluenceTracker

## 🚀 Quick Deploy Options

### Option 1: Streamlit Cloud (Recommended)
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository: `amullyapatil/influence-tracker`
5. Set the main file path: `app.py`
6. Click "Deploy"

### Option 2: Railway
1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically detect it's a Python app
6. Add environment variables in the Railway dashboard

### Option 3: Render
1. Go to [render.com](https://render.com)
2. Sign in with GitHub
3. Click "New" → "Web Service"
4. Connect your repository
5. Set build command: `pip install -r requirements.txt`
6. Set start command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

## 🔧 Environment Variables Setup

Add these environment variables to your deployment platform:

```
YOUTUBE_API_KEY=your_youtube_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here (optional)
```

## 📋 Prerequisites

1. **YouTube API Key**: Get from [Google Cloud Console](https://console.cloud.google.com/)
2. **Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
3. **OpenAI API Key** (optional): Get from [OpenAI Platform](https://platform.openai.com/api-keys)

## 🎯 GitHub Pages Alternative

Since GitHub Pages only supports static websites, here are better alternatives for your Python app:

- **Streamlit Cloud**: Free, specifically designed for Streamlit apps
- **Railway**: Free tier available, easy deployment
- **Render**: Free tier available, good for Python apps
- **Heroku**: Paid, but very reliable

## 🔗 Your App URL

Once deployed, your app will be available at:
- Streamlit Cloud: `https://your-app-name.streamlit.app`
- Railway: `https://your-app-name.railway.app`
- Render: `https://your-app-name.onrender.com`

## 📝 Next Steps

1. Choose a deployment platform from above
2. Follow the platform-specific instructions
3. Add your API keys as environment variables
4. Deploy and share your app URL!

## 🆘 Troubleshooting

- **Port Issues**: Make sure your platform uses the `$PORT` environment variable
- **API Key Errors**: Verify all environment variables are set correctly
- **Dependencies**: Ensure `requirements.txt` is up to date
