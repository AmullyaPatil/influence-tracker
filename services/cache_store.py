"""
Local JSON cache storage for posts and metadata.
"""
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import streamlit as st


def ensure_data_directory():
    """Ensure the data directory exists."""
    os.makedirs('data', exist_ok=True)


def load_cache() -> Dict:
    """Load cached data from JSON file."""
    ensure_data_directory()
    cache_file = 'data/posts.json'
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.warning(f"⚠️ Error loading cache: {e}")
    
    # Return default structure if file doesn't exist or is corrupted
    return {
        "posts": [],
        "meta": {
            "last_run": None,
            "total_posts": 0,
            "last_updated": None
        }
    }


def save_cache(data: Dict) -> None:
    """Save data to cache file."""
    ensure_data_directory()
    cache_file = 'data/posts.json'
    
    try:
        # Update metadata
        data['meta']['last_updated'] = datetime.now().isoformat()
        data['meta']['total_posts'] = len(data['posts'])
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        st.error(f"❌ Error saving cache: {e}")


def upsert_posts(new_posts: List[Dict], ignore_old: bool = True) -> None:
    """
    Add new posts to cache, avoiding duplicates.
    
    Args:
        new_posts: List of new post dictionaries
        ignore_old: Skip posts older than 7 days
    """
    cache = load_cache()
    existing_ids = {post['post_id'] for post in cache['posts']}
    
    # Filter out duplicates and old posts
    posts_to_add = []
    skipped_count = 0
    
    for post in new_posts:
        if post['post_id'] in existing_ids:
            skipped_count += 1
            continue
            
        # Check if post is too old (optional)
        if ignore_old:
            try:
                published_date = datetime.fromisoformat(post['published_at'].replace('Z', '+00:00'))
                if published_date < datetime.now(published_date.tzinfo) - timedelta(days=7):
                    skipped_count += 1
                    continue
            except:
                pass  # If date parsing fails, include the post
        
        posts_to_add.append(post)
    
    # Add new posts
    cache['posts'].extend(posts_to_add)
    
    # Update metadata
    cache['meta']['last_run'] = datetime.now().isoformat()
    
    # Save updated cache
    save_cache(cache)
    
    if skipped_count > 0:
        st.info(f"ℹ️ Skipped {skipped_count} duplicate/old posts")


def get_recent_posts(hours: int = 48) -> List[Dict]:
    """Get posts from the last N hours."""
    cache = load_cache()
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    recent_posts = []
    for post in cache['posts']:
        try:
            published_date = datetime.fromisoformat(post['published_at'].replace('Z', '+00:00'))
            if published_date >= cutoff_time:
                recent_posts.append(post)
        except:
            # If date parsing fails, include the post
            recent_posts.append(post)
    
    return recent_posts


def clear_cache() -> None:
    """Clear all cached data."""
    cache_file = 'data/posts.json'
    if os.path.exists(cache_file):
        os.remove(cache_file)
        st.success("🗑️ Cache cleared successfully")
    else:
        st.info("ℹ️ No cache file to clear")
