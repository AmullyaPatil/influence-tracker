"""
Trend analysis and executive brief generation.
"""
from collections import Counter
from typing import Dict, List, Tuple
import streamlit as st


def aggregate_trends(posts: List[Dict]) -> Tuple[Counter, List[Tuple[str, int]]]:
    """
    Aggregate trends from posts and return top 5.
    
    Args:
        posts: List of post dictionaries
        
    Returns:
        Tuple of (Counter object, list of top 5 trends with counts)
    """
    all_trends = []
    
    for post in posts:
        trends = post.get('trends', [])
        if isinstance(trends, str):
            # Handle case where trends might be stored as comma-separated string
            trends = [t.strip() for t in trends.split(',') if t.strip()]
        
        # Normalize trends (lowercase, remove common prefixes)
        normalized_trends = []
        for trend in trends:
            if isinstance(trend, str):
                trend = trend.lower().strip()
                # Remove common prefixes
                if trend.startswith(('the ', 'a ', 'an ')):
                    trend = trend[trend.find(' ') + 1:]
                normalized_trends.append(trend)
        
        all_trends.extend(normalized_trends)
    
    # Count occurrences
    trend_counter = Counter(all_trends)
    
    # Get top 5 trends
    top_trends = trend_counter.most_common(5)
    
    return trend_counter, top_trends


def compute_sentiment_mix(posts: List[Dict]) -> Dict[str, int]:
    """
    Compute sentiment distribution across posts.
    
    Args:
        posts: List of post dictionaries
        
    Returns:
        Dictionary with sentiment counts
    """
    sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
    
    for post in posts:
        sentiment = post.get('sentiment', 'neutral').lower()
        if sentiment in sentiment_counts:
            sentiment_counts[sentiment] += 1
        else:
            sentiment_counts['neutral'] += 1
    
    return sentiment_counts


def make_brief(posts: List[Dict], top_trends: List[Tuple[str, int]], sentiment_mix: Dict[str, int]) -> str:
    """
    Generate an executive brief summarizing key insights.
    
    Args:
        posts: List of post dictionaries
        top_trends: Top 5 trends with counts
        sentiment_mix: Sentiment distribution
        
    Returns:
        Executive brief as a string
    """
    total_posts = len(posts)
    
    if total_posts == 0:
        return "No recent content available for analysis."
    
    # Get dominant sentiment
    dominant_sentiment = max(sentiment_mix.items(), key=lambda x: x[1])[0]
    
    # Get top trend
    top_trend, top_count = top_trends[0] if top_trends else ("", 0)
    
    # Generate brief
    brief_parts = []
    
    # Opening statement
    brief_parts.append(f"Analysis of {total_posts} recent posts reveals ")
    
    # Sentiment insight
    if sentiment_mix[dominant_sentiment] > total_posts * 0.6:
        brief_parts.append(f"a predominantly {dominant_sentiment} sentiment ({sentiment_mix[dominant_sentiment]}/{total_posts} posts).")
    else:
        brief_parts.append(f"a mixed sentiment landscape with {sentiment_mix['positive']} positive, {sentiment_mix['neutral']} neutral, and {sentiment_mix['negative']} negative posts.")
    
    # Trend insight
    if top_trends:
        brief_parts.append(f" The most prominent trend is '{top_trend}' (appearing in {top_count} posts), followed by '{top_trends[1][0] if len(top_trends) > 1 else ''}' and '{top_trends[2][0] if len(top_trends) > 2 else ''}'.")
    
    # Action recommendation
    if dominant_sentiment == 'positive':
        brief_parts.append(" Consider amplifying content around these trending topics to maintain momentum.")
    elif dominant_sentiment == 'negative':
        brief_parts.append(" Monitor these trends closely and prepare response strategies if needed.")
    else:
        brief_parts.append(" Continue monitoring these trends to identify emerging opportunities.")
    
    return " ".join(brief_parts)


def format_trends_for_display(top_trends: List[Tuple[str, int]]) -> str:
    """Format trends for display in the UI."""
    if not top_trends:
        return "No trends identified"
    
    formatted = []
    for i, (trend, count) in enumerate(top_trends, 1):
        formatted.append(f"{i}. {trend.title()} ({count})")
    
    return "\n".join(formatted)
