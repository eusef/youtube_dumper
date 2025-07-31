#!/usr/bin/env python3
"""
List all videos on a YouTube channel with comprehensive metadata.

Prerequisites
-------------
1. Get a YouTube Data API v3 key:
   https://console.cloud.google.com/apis/library/youtube.googleapis.com
2. Create a .env file in the current directory with:
   YT_API_KEY=YOUR_API_KEY

Usage
-----
python yt_dumper.py CHANNEL_ID [--json]
python yt_dumper.py CHANNEL_ID --json [output_file.json]
"""
import os
import sys
import requests
import json
import csv
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables from .env file (supports named pipes)
def load_env_from_pipe():
    """Load environment variables from .env file, handling named pipes."""
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    except Exception as e:
        print(f"Warning: Could not read .env file: {e}")
    return env_vars

# Load environment variables
env_vars = load_env_from_pipe()
API_KEY = env_vars.get("YT_API_KEY") or os.getenv("YT_API_KEY")

# Debug: Check if API key was loaded (only show first few characters for security)
if API_KEY:
    print(f"API key loaded successfully: {API_KEY[:10]}...")
else:
    print("No API key found")
BASE_URL = "https://www.googleapis.com/youtube/v3"

if not API_KEY:
    sys.exit("Error: YT_API_KEY not found in .env file or environment variables")

def search_channel_by_name(channel_name: str) -> str:
    """Search for a channel by name and return the channel ID."""
    r = requests.get(
        f"{BASE_URL}/search",
        params={
            "part": "snippet",
            "q": channel_name,
            "type": "channel",
            "maxResults": 1,
            "key": API_KEY
        },
        timeout=10
    )
    
    try:
        data = r.json()
        if r.status_code != 200:
            error_message = data.get('error', {}).get('message', 'Unknown error')
            sys.exit(f"Search API Error: {error_message}")
        
        items = data.get("items", [])
        if not items:
            sys.exit(f"No channel found with name: {channel_name}")
        
        channel_id = items[0]["snippet"]["channelId"]
        channel_title = items[0]["snippet"]["title"]
        print(f"Found channel: '{channel_title}' (ID: {channel_id})")
        return channel_id
    except KeyError as e:
        sys.exit(f"Unexpected search API response format: {e}")
    except json.JSONDecodeError:
        sys.exit(f"Invalid JSON response from search API: {r.text}")

def get_uploads_playlist_id(channel_id: str) -> str:
    r = requests.get(
        f"{BASE_URL}/channels",
        params={
            "part": "contentDetails",
            "id": channel_id,
            "key": API_KEY
        },
        timeout=10
    )
    
    if r.status_code == 403:
        error_data = r.json()
        error_message = error_data.get('error', {}).get('message', 'Unknown error')
        if 'API key not valid' in error_message or 'quota' in error_message.lower():
            sys.exit(f"API Error: {error_message}\nPlease check your API key and ensure YouTube Data API v3 is enabled.")
        else:
            sys.exit(f"API Error: {error_message}")
    elif r.status_code == 400:
        error_data = r.json()
        error_message = error_data.get('error', {}).get('message', 'Invalid request')
        sys.exit(f"Invalid request: {error_message}")
    
    try:
        data = r.json()
        if r.status_code != 200:
            error_message = data.get('error', {}).get('message', 'Unknown error')
            if 'API key not valid' in error_message or 'quota' in error_message.lower():
                sys.exit(f"API Error: {error_message}\nPlease check your API key and ensure YouTube Data API v3 is enabled.")
            else:
                sys.exit(f"API Error: {error_message}")
        
        items = data.get("items", [])
        if not items:
            sys.exit("Channel not found or not public.")
        return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    except KeyError as e:
        sys.exit(f"Unexpected API response format: {e}")
    except json.JSONDecodeError:
        sys.exit(f"Invalid JSON response from API: {r.text}")

def get_all_video_ids(playlist_id: str) -> list[str]:
    ids, page_token = [], ""
    while True:
        r = requests.get(
            f"{BASE_URL}/playlistItems",
            params={
                "part": "contentDetails",
                "playlistId": playlist_id,
                "maxResults": 50,
                "pageToken": page_token,
                "key": API_KEY
            },
            timeout=10
        )
        r.raise_for_status()
        data = r.json()
        ids.extend(item["contentDetails"]["videoId"] for item in data["items"])
        page_token = data.get("nextPageToken", "")
        if not page_token:
            break
    return ids

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def fetch_metadata(video_ids: list[str]) -> list[dict]:
    """Fetch comprehensive metadata for videos without any truncation."""
    all_videos = []
    for batch in chunks(video_ids, 50):
        r = requests.get(
            f"{BASE_URL}/videos",
            params={
                "part": "snippet,statistics,contentDetails,status",
                "id": ",".join(batch),
                "key": API_KEY
            },
            timeout=10
        )
        r.raise_for_status()
        all_videos.extend(r.json()["items"])
    return all_videos

def format_duration(duration: str) -> str:
    """Convert ISO 8601 duration to readable format."""
    import re
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if not match:
        return duration
    
    hours, minutes, seconds = match.groups()
    hours = int(hours) if hours else 0
    minutes = int(minutes) if minutes else 0
    seconds = int(seconds) if seconds else 0
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def export_to_csv(videos: list[dict], channel_id: str, output_file: str = None):
    """Export videos to CSV format."""
    if not output_file:
        output_file = f"{channel_id}_videos.csv"
    
    fieldnames = [
        'Video ID', 'Title', 'URL', 'Published Date', 'Age (days)', 
        'Duration', 'Views', 'Likes', 'Comments', 'Description', 
        'Tags', 'Category', 'Privacy Status', 'Made for Kids'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for video in videos:
            snippet = video["snippet"]
            statistics = video.get("statistics", {})
            content_details = video.get("contentDetails", {})
            status = video.get("status", {})
            
            # Calculate age
            published = datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            age_days = (now - published).days
            
            # Truncate description to avoid CSV issues
            description = snippet.get('description', 'No description')
            if len(description) > 500:
                description = description[:500] + "..."
            
            # Clean tags for CSV
            tags = ', '.join(snippet.get('tags', []))
            if len(tags) > 200:
                tags = tags[:200] + "..."
            
            row = {
                'Video ID': video['id'],
                'Title': snippet['title'],
                'URL': f"https://www.youtube.com/watch?v={video['id']}",
                'Published Date': snippet['publishedAt'],
                'Age (days)': age_days,
                'Duration': format_duration(content_details.get('duration', 'PT0S')),
                'Views': statistics.get('viewCount', 'N/A'),
                'Likes': statistics.get('likeCount', 'N/A'),
                'Comments': statistics.get('commentCount', 'N/A'),
                'Description': description,
                'Tags': tags,
                'Category': snippet.get('categoryId', 'N/A'),
                'Privacy Status': status.get('privacyStatus', 'N/A'),
                'Made for Kids': status.get('madeForKids', 'N/A')
            }
            writer.writerow(row)
    
    print(f"CSV data exported to {output_file}")

def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python yt_dumper.py CHANNEL_NAME_OR_ID [--json] [output_file.csv|.json]")
    
    channel_input = sys.argv[1]
    export_json = "--json" in sys.argv
    output_file = None
    
    # Check for output file argument
    for i, arg in enumerate(sys.argv[2:], 2):
        if not arg.startswith("--") and arg != "--json":
            output_file = arg
            break
    
    # Check if input is a channel ID (starts with UC) or a channel name
    if channel_input.startswith("UC") and len(channel_input) == 24:
        # It's already a channel ID
        channel_id = channel_input
        print(f"Using channel ID: {channel_id}")
    else:
        # It's a channel name, search for it
        print(f"Searching for channel: {channel_input}")
        channel_id = search_channel_by_name(channel_input)
    
    uploads_id = get_uploads_playlist_id(channel_id)
    video_ids = get_all_video_ids(uploads_id)
    videos = fetch_metadata(video_ids)
    
    # Sort by publish date (newest first)
    videos.sort(key=lambda x: x["snippet"]["publishedAt"], reverse=True)
    
    print(f"Found {len(videos)} videos on channel {channel_id}")
    
    if export_json:
        # Export complete data to JSON
        output_data = {
            "channel_id": channel_id,
            "total_videos": len(videos),
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "videos": videos
        }
        
        json_output = json.dumps(output_data, indent=2, ensure_ascii=False)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_output)
            print(f"JSON data exported to {output_file}")
        else:
            print(json_output)
    else:
        # Export to CSV by default
        export_to_csv(videos, channel_id, output_file)

if __name__ == "__main__":
    main()

