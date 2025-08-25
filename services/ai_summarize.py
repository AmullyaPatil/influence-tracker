"""
AI summarization service using Gemini (default) and OpenAI (fallback).
"""
import os
import json
import time
from typing import Dict, Optional
import google.generativeai as genai
import openai
import streamlit as st


def configure_ai_services():
    """Configure AI services with API keys."""
    # Configure Gemini
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key:
        genai.configure(api_key=gemini_key)
    
    # Configure OpenAI (optional)
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        openai.api_key = openai_key


def summarize_text(text: str, niche: str, model: str = "gemini") -> Dict:
    """
    Summarize text using AI and extract sentiment and trends.
    
    Args:
        text: Text to summarize
        niche: Business niche for context
        model: AI model to use ("gemini" or "openai")
        
    Returns:
        Dictionary with summary, sentiment, and trends
    """
    if model == "openai" and os.getenv('OPENAI_API_KEY'):
        return _summarize_openai(text, niche)
    else:
        return _summarize_gemini(text, niche)


def _summarize_gemini(text: str, niche: str) -> Dict:
    """Summarize using Google Gemini."""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Enhanced niche-aware prompting
        if niche.lower() == "gaming":
            prompt = f"""You are an analyst for a GAMING brand team. Focus on gaming industry insights, player behavior, gaming trends, and gaming-related business opportunities.

Analyze this YouTube video content from a GAMING perspective and return a JSON response with exactly these keys:
- summary: 50-80 word summary focused on GAMING aspects, player engagement, or gaming industry insights
- sentiment: one of [positive, neutral, negative] 
- trends: array of 3-5 short phrases identifying GAMING trends, player preferences, or gaming industry topics

Input content:
{text}

Return only valid JSON:"""
        else:
            prompt = f"""You are an analyst for a brand team in the '{niche}' niche. 
        
Analyze this YouTube video content and return a JSON response with exactly these keys:
- summary: 50-80 word summary of the main content
- sentiment: one of [positive, neutral, negative] 
- trends: array of 3-5 short phrases identifying key trends/topics

Input content:
{text}

Return only valid JSON:"""

        response = model.generate_content(prompt)
        result = response.text.strip()
        
        # Try to extract JSON from response
        try:
            # Find JSON in the response
            start = result.find('{')
            end = result.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = result[start:end]
                parsed = json.loads(json_str)
                
                # Validate required keys
                required_keys = ['summary', 'sentiment', 'trends']
                if all(key in parsed for key in required_keys):
                    return {
                        'summary': parsed['summary'][:300],
                        'sentiment': parsed['sentiment'].lower(),
                        'trends': parsed['trends'][:5]
                    }
        except:
            pass
        
        # Fallback if JSON parsing fails
        return {
            'summary': text[:300] + "..." if len(text) > 300 else text,
            'sentiment': 'neutral',
            'trends': []
        }
        
    except Exception as e:
        st.warning(f"⚠️ Gemini API error: {e}")
        return {
            'summary': text[:300] + "..." if len(text) > 300 else text,
            'sentiment': 'neutral',
            'trends': []
        }


def _summarize_openai(text: str, niche: str) -> Dict:
    """Summarize using OpenAI GPT."""
    try:
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Enhanced niche-aware prompting for OpenAI too
        if niche.lower() == "gaming":
            system_prompt = "You are an analyst for a GAMING brand team. Focus on gaming industry insights, player behavior, gaming trends, and gaming-related business opportunities. Return only valid JSON."
        else:
            system_prompt = f"You are an analyst for a brand team in the '{niche}' niche. Return only valid JSON."
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"""Analyze this YouTube video content and return a JSON response with exactly these keys:
- summary: 50-80 word summary {'focused on GAMING aspects, player engagement, or gaming industry insights' if niche.lower() == 'gaming' else 'of the main content'}
- sentiment: one of [positive, neutral, negative] 
- trends: array of 3-5 short phrases identifying {'GAMING trends, player preferences, or gaming industry topics' if niche.lower() == 'gaming' else 'key trends/topics'}

Input content:
{text}"""
                }
            ],
            temperature=0.3
        )
        
        result = response.choices[0].message.content.strip()
        
        try:
            parsed = json.loads(result)
            return {
                'summary': parsed['summary'][:300],
                'sentiment': parsed['sentiment'].lower(),
                'trends': parsed['trends'][:5]
            }
        except:
            return _summarize_gemini(text, niche)  # Fallback to Gemini
            
    except Exception as e:
        st.warning(f"⚠️ OpenAI API error: {e}")
        return _summarize_gemini(text, niche)  # Fallback to Gemini


def rate_limit_sleep(seconds: int):
    """Sleep for rate limiting between API calls."""
    if seconds > 0:
        with st.spinner(f"⏳ Waiting {seconds}s for rate limiting..."):
            time.sleep(seconds)
