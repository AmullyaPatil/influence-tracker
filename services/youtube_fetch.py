"""
YouTube Data API service for fetching channel videos.
"""
import os
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import streamlit as st


def fetch_youtube(channel_id: str, api_key: str, max_results: int = 3) -> List[Dict]:
    """
    Fetch latest videos from a YouTube channel.
    
    Args:
        channel_id: YouTube channel ID (UC...)
        api_key: YouTube Data API v3 key
        max_results: Maximum number of videos to fetch
        
    Returns:
        List of video dictionaries with post_id, title, url, published_at, raw_text
    """
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Search for videos from the channel
        search_response = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            order="date",
            type="video",
            maxResults=max_results
        ).execute()
        
        videos = []
        for item in search_response.get('items', []):
            snippet = item['snippet']
            
            # Get video description
            video_response = youtube.videos().list(
                part="snippet",
                id=item['id']['videoId']
            ).execute()
            
            description = ""
            if video_response.get('items'):
                description = video_response['items'][0]['snippet'].get('description', '')
            
            # Combine title and description for AI analysis
            raw_text = f"{snippet['title']}\n\n{description}"[:2000]
            
            video_data = {
                'post_id': item['id']['videoId'],
                'title': snippet['title'],
                'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                'published_at': snippet['publishedAt'],
                'raw_text': raw_text,
                'channel_title': snippet.get('channelTitle', 'Unknown Channel')
            }
            videos.append(video_data)
            
        return videos
        
    except HttpError as e:
        if e.resp.status == 403:
            st.error(f"❌ YouTube API quota exceeded or invalid API key for channel {channel_id}")
        elif e.resp.status == 400:
            st.error(f"❌ Invalid channel ID: {channel_id}")
        else:
            st.error(f"❌ YouTube API error: {e}")
        return []
        
    except Exception as e:
        st.error(f"❌ Unexpected error fetching from {channel_id}: {e}")
        return []


def validate_channel_id(channel_id: str) -> bool:
    """Validate YouTube channel ID format."""
    return channel_id.startswith('UC') and len(channel_id) == 24
