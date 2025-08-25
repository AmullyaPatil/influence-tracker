"""
InfluenceTracker - AI-Powered YouTube Trend Analysis
A Streamlit app for tracking influencer/competitor content and generating trend briefs.
"""
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# Import our services
from services.youtube_fetch import fetch_youtube, validate_channel_id
from services.ai_summarize import summarize_text, configure_ai_services, rate_limit_sleep
from services.cache_store import upsert_posts, get_recent_posts, clear_cache, load_cache
from services.brief import aggregate_trends, compute_sentiment_mix, make_brief, format_trends_for_display

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="InfluenceTracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .section-divider {
        border-top: 2px solid #e9ecef;
        margin: 2rem 0;
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 InfluenceTracker</h1>
        <p>AI-Powered YouTube Trend Analysis for Brand Teams</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Keys
        youtube_api_key = st.text_input(
            "YouTube API Key",
            value=os.getenv('YOUTUBE_API_KEY', ''),
            type="password",
            help="Get from Google Cloud Console"
        )
        
        gemini_api_key = st.text_input(
            "Gemini API Key",
            value=os.getenv('GEMINI_API_KEY', ''),
            type="password",
            help="Get from Google AI Studio"
        )
        
        openai_api_key = st.text_input(
            "OpenAI API Key (Optional)",
            value=os.getenv('OPENAI_API_KEY', ''),
            type="password",
            help="Fallback if Gemini fails"
        )
        
        # Settings
        st.subheader("📋 Settings")
        videos_per_channel = st.slider("Videos per channel", 1, 5, 3)
        rate_limit_delay = st.slider("Rate limit delay (seconds)", 2, 30, 5)
        ignore_old_posts = st.checkbox("Ignore old posts (>7 days)", value=True)
        
        # Cache management
        st.subheader("🗄️ Cache")
        if st.button("Clear Cache"):
            clear_cache()
            st.rerun()
        
        # Cache stats
        cache = load_cache()
        st.metric("Cached Posts", cache['meta']['total_posts'])
        if cache['meta']['last_run']:
            st.metric("Last Run", cache['meta']['last_run'][:19])
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🎯 Input")
        
        # Channel IDs input
        channel_ids_text = st.text_area(
            "YouTube Channel IDs (one per line, UC... format)",
            value="UC_x5XG1OV2P6uZZ5FSM9Ttw\nUCBJycsmduvYEL83R_U4JriQ",
            height=100,
            help="Enter YouTube channel IDs in UC... format, one per line"
        )
        
        # Niche input
        niche = st.text_input(
            "Business Niche",
            value="Technology & Innovation",
            help="Context for AI analysis (e.g., 'Fashion', 'Tech', 'Food')"
        )
        
        # AI Model selection
        ai_model = st.selectbox(
            "AI Model",
            ["gemini", "openai"],
            help="Primary AI model for summarization"
        )
        
        # Action buttons
        col1_1, col1_2, col1_3 = st.columns(3)
        
        with col1_1:
            if st.button("🚀 Fetch + Summarize", type="primary"):
                if not youtube_api_key or not gemini_api_key:
                    st.error("❌ Please provide YouTube and Gemini API keys")
                else:
                    process_channels(channel_ids_text, niche, videos_per_channel, 
                                  rate_limit_delay, ignore_old_posts, ai_model)
        
        with col1_2:
            if st.button("📊 Generate Brief"):
                generate_trend_brief()
        
        with col1_3:
            if st.button("💾 Download CSV"):
                download_csv()
    
    with col2:
        st.header("📈 Quick Stats")
        
        # Load recent posts for stats
        recent_posts = get_recent_posts(48)
        
        if recent_posts:
            # Sentiment breakdown
            sentiment_counts = compute_sentiment_mix(recent_posts)
            
            st.subheader("Sentiment (48h)")
            for sentiment, count in sentiment_counts.items():
                if count > 0:
                    st.metric(sentiment.title(), count)
            
            # Top trends preview
            if recent_posts:
                _, top_trends = aggregate_trends(recent_posts)
                if top_trends:
                    st.subheader("Top Trends")
                    for i, (trend, count) in enumerate(top_trends[:3], 1):
                        st.metric(f"{i}. {trend.title()}", count)
        else:
            st.info("No recent posts. Fetch some content to see stats!")
    
    # Results section
    if 'processed_posts' in st.session_state:
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.header("📋 Analysis Results")
        
        # Display processed posts
        display_results(st.session_state.processed_posts)
        
        # Generate and display brief
        if st.session_state.processed_posts:
            generate_trend_brief()


def process_channels(channel_ids_text, niche, videos_per_channel, rate_limit_delay, ignore_old_posts, ai_model):
    """Process YouTube channels and generate summaries."""
    # Configure AI services
    configure_ai_services()
    
    # Parse channel IDs
    channel_ids = [cid.strip() for cid in channel_ids_text.split('\n') if cid.strip()]
    valid_channels = [cid for cid in channel_ids if validate_channel_id(cid)]
    
    if not valid_channels:
        st.error("❌ No valid channel IDs found. Please use UC... format.")
        return
    
    if len(valid_channels) != len(channel_ids):
        st.warning(f"⚠️ {len(channel_ids) - len(valid_channels)} invalid channel IDs skipped")
    
    # Process each channel
    all_posts = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, channel_id in enumerate(valid_channels):
        status_text.text(f"Processing channel {i+1}/{len(valid_channels)}: {channel_id}")
        
        # Fetch videos
        videos = fetch_youtube(channel_id, os.getenv('YOUTUBE_API_KEY'), videos_per_channel)
        
        if videos:
            # Process each video
            for j, video in enumerate(videos):
                status_text.text(f"Analyzing video {j+1}/{len(videos)} from {channel_id}")
                
                # Rate limiting
                if j > 0:  # Don't sleep before first video
                    rate_limit_sleep(rate_limit_delay)
                
                # Generate AI summary
                ai_result = summarize_text(video['raw_text'], niche, ai_model)
                
                # Create post object
                post = {
                    'platform': 'YouTube',
                    'channel_id': channel_id,
                    'post_id': video['post_id'],
                    'title': video['title'],
                    'url': video['url'],
                    'published_at': video['published_at'],
                    'summary': ai_result['summary'],
                    'sentiment': ai_result['sentiment'],
                    'trends': ','.join(ai_result['trends']),
                    'cached_at': datetime.now().isoformat(),
                    'channel_title': video.get('channel_title', 'Unknown')
                }
                
                all_posts.append(post)
        
        progress_bar.progress((i + 1) / len(valid_channels))
    
    # Save to cache
    if all_posts:
        upsert_posts(all_posts, ignore_old_posts)
        st.session_state.processed_posts = all_posts
        st.success(f"✅ Successfully processed {len(all_posts)} videos from {len(valid_channels)} channels")
    else:
        st.warning("⚠️ No videos were processed")
    
    progress_bar.empty()
    status_text.empty()


def display_results(posts):
    """Display analysis results."""
    if not posts:
        return
    
    # Create DataFrame
    df = pd.DataFrame(posts)
    
    # Display table
    st.subheader("📊 Video Analysis")
    display_df = df[['title', 'sentiment', 'trends', 'url', 'channel_title']].copy()
    display_df['title'] = display_df['title'].str[:60] + '...'
    display_df['trends'] = display_df['trends'].str[:50] + '...'
    
    st.dataframe(display_df, use_container_width=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Sentiment chart
        sentiment_counts = df['sentiment'].value_counts()
        fig_sentiment = px.bar(
            x=sentiment_counts.index,
            y=sentiment_counts.values,
            title="Sentiment Distribution",
            color=sentiment_counts.index,
            color_discrete_map={'positive': '#28a745', 'neutral': '#6c757d', 'negative': '#dc3545'}
        )
        st.plotly_chart(fig_sentiment, use_container_width=True)
    
    with col2:
        # Trends chart
        all_trends = []
        for trends_str in df['trends']:
            if trends_str:
                trends = [t.strip() for t in trends_str.split(',') if t.strip()]
                all_trends.extend(trends)
        
        if all_trends:
            trend_counts = pd.Series(all_trends).value_counts().head(8)
            fig_trends = px.bar(
                x=trend_counts.values,
                y=trend_counts.index,
                orientation='h',
                title="Top Trends",
                color=trend_counts.values,
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig_trends, use_container_width=True)


def generate_trend_brief():
    """Generate and display trend brief."""
    recent_posts = get_recent_posts(48)
    
    if not recent_posts:
        st.warning("⚠️ No recent posts available for brief generation")
        return
    
    # Analyze trends and sentiment
    _, top_trends = aggregate_trends(recent_posts)
    sentiment_mix = compute_sentiment_mix(recent_posts)
    
    # Generate brief
    brief = make_brief(recent_posts, top_trends, sentiment_mix)
    
    # Display results
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.header("📋 Executive Brief (48h)")
    
    # Brief text
    st.markdown(f"""
    <div class="metric-card">
        <h4>🎯 Key Insights</h4>
        <p>{brief}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Top trends
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 Top 5 Trends")
        st.text(format_trends_for_display(top_trends))
    
    with col2:
        st.subheader("😊 Sentiment Mix")
        for sentiment, count in sentiment_mix.items():
            if count > 0:
                percentage = (count / len(recent_posts)) * 100
                st.metric(sentiment.title(), f"{count} ({percentage:.1f}%)")


def download_csv():
    """Download all cached posts as CSV."""
    cache = load_cache()
    
    if not cache['posts']:
        st.warning("⚠️ No posts available for download")
        return
    
    df = pd.DataFrame(cache['posts'])
    
    # Convert to CSV
    csv = df.to_csv(index=False)
    
    # Download button
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"influence_tracker_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )


if __name__ == "__main__":
    main()
