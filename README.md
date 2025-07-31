# YouTube Channel Video Dumper

A Python script that extracts comprehensive video metadata from any YouTube channel and exports it to CSV or JSON format. Supports channel name search and handles named pipes for secure API key management.

## Features

- 🔍 **Channel Name Search**: Use human-readable channel names instead of channel IDs
- 📊 **CSV Export**: Default output format perfect for data analysis
- 📄 **JSON Export**: Complete metadata export with `--json` flag
- 🔐 **Secure API Key**: Supports named pipes (1Password integration)
- 📈 **Comprehensive Data**: Video ID, title, URL, publish date, views, likes, comments, duration, description, tags, and more
- 🎯 **Smart Detection**: Automatically detects channel IDs vs channel names
- ⚡ **Efficient**: Handles large channels with pagination

## Prerequisites

1. **Python 3.7+** installed on your system
2. **YouTube Data API v3** key from Google Cloud Console

### Getting a YouTube API Key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **YouTube Data API v3**:
   - Go to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"
4. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy your API key

## Installation

1. **Clone or download the script**:
   ```bash
   git clone <repository-url>
   cd youtube_dumper
   ```

2. **Install dependencies**:
   ```bash
   python3 -m venv .venv
   pip install -r requirements.txt
   ```

3. **Set up your API key**:

   **Option A: Using a named pipe (recommended for 1Password Environments users)**
   ```bash
   # In 1Pasword - Create a named Environment pipe that 1Password can write to
   # .env
   # 1Password will write your API key to this pipe
   ```

   **Option B: Using a regular .env file**
   ```bash
   echo "YT_API_KEY=your_api_key_here" > .env
   ```

   **Option C: Environment variable**
   ```bash
   export YT_API_KEY=your_api_key_here
   ```

## Usage

### Basic Usage

```bash
# Export to CSV using channel name
python yt_dumper.py "yousuckatprogramming"

# Export to CSV using channel ID
python yt_dumper.py UCX6OQ3DkcsbYNE6H8uQQuVA

# Export to JSON
python yt_dumper.py "yousuckatprogramming" --json

# Custom output filename
python yt_dumper.py "yousuckatprogramming" my_videos.csv
python yt_dumper.py "yousuckatprogramming" --json my_data.json
```

### Output Files

- **Default CSV**: `{channel_id}_videos.csv`
- **Default JSON**: Prints to console (use filename for file output)
- **Custom filename**: Specify any filename as the last argument

### CSV Output Columns

| Column | Description |
|--------|-------------|
| Video ID | YouTube video identifier |
| Title | Video title |
| URL | Direct YouTube link |
| Published Date | ISO 8601 timestamp |
| Age (days) | Days since publication |
| Duration | Formatted duration (MM:SS or HH:MM:SS) |
| Views | View count |
| Likes | Like count |
| Comments | Comment count |
| Description | Video description (truncated to 500 chars) |
| Tags | Video tags (truncated to 200 chars) |
| Category | YouTube category ID |
| Privacy Status | public/private/unlisted |
| Made for Kids | true/false |

### JSON Output Structure

```json
{
  "channel_id": "UCMN0a7GHQnC6H74SmCGSmdw",
  "total_videos": 956,
  "exported_at": "2024-07-31T16:19:00.123456+00:00",
  "videos": [
    {
      "id": "video_id",
      "snippet": {
        "title": "Video Title",
        "description": "Full description...",
        "publishedAt": "2024-07-30T17:40:43Z",
        "tags": ["tag1", "tag2"],
        "categoryId": "28"
      },
      "statistics": {
        "viewCount": "9177",
        "likeCount": "421",
        "commentCount": "8"
      },
      "contentDetails": {
        "duration": "PT1M39S"
      },
      "status": {
        "privacyStatus": "public",
        "madeForKids": false
      }
    }
  ]
}
```

## Examples

### Export MrBeast's channel to CSV
```bash
python yt_dumper.py "MrBeast"
```

### Export a gaming channel to JSON
```bash
python yt_dumper.py "PewDiePie" --json gaming_videos.json
```

### Export using channel ID
```bash
python yt_dumper.py UCX6OQ3DkcsbYNE6H8uQQuVA custom_name.csv
```

## Troubleshooting

### "API key not found" error
- Ensure your `.env` file exists and contains `YT_API_KEY=your_key`
- Check that the named pipe is readable if using 1Password
- Verify the API key is valid and not expired

### "Channel not found" error
- Check the channel name spelling
- Ensure the channel is public
- Try using the channel ID instead of name

### "API quota exceeded" error
- YouTube Data API has daily quotas
- Wait until quota resets or upgrade your API plan
- Consider using multiple API keys for large channels

### "Permission denied" on named pipe
- Ensure the pipe has correct permissions
- If using 1Password, make sure it's configured to write to the pipe

## API Quotas

The YouTube Data API v3 has the following quotas:
- **Free tier**: 10,000 units per day
- **Each video fetch**: ~1 unit
- **Each channel search**: ~100 units
- **Each playlist fetch**: ~1 unit per video

For large channels, you may need to:
- Upgrade to a paid API plan
- Use multiple API keys
- Implement rate limiting

## Dependencies

- `requests>=2.25.0` - HTTP requests
- `python-dotenv>=0.19.0` - Environment variable loading
- `csv` - CSV file handling (built-in)
- `json` - JSON handling (built-in)

## License

This project is open source. Feel free to modify and distribute.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your API key is valid
3. Ensure the YouTube Data API v3 is enabled
4. Check that the channel is public and accessible 