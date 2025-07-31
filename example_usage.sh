#!/bin/bash

# Example usage script for YouTube Channel Video Dumper
# Make sure you have set up your API key before running these examples

echo "YouTube Channel Video Dumper - Example Usage"
echo "============================================"
echo ""

# Example 1: Export a channel to CSV (default)
echo "Example 1: Export 'You Suck at Programming' to CSV"
python yt_dumper.py "yousuckatprogramming"
echo ""

# Example 2: Export to JSON
echo "Example 2: Export to JSON format"
python yt_dumper.py "yousuckatprogramming" --json
echo ""

# Example 3: Custom filename
echo "Example 3: Export with custom filename"
python yt_dumper.py "yousuckatprogramming" my_custom_videos.csv
echo ""

# Example 4: Using channel ID
echo "Example 4: Using channel ID instead of name"
python yt_dumper.py UCX6OQ3DkcsbYNE6H8uQQuVA channel_id_example.csv
echo ""

# Example 5: JSON with custom filename
echo "Example 5: JSON export with custom filename"
python yt_dumper.py "yousuckatprogramming" --json my_data.json
echo ""

echo "All examples completed!"
echo "Check the generated files in the current directory." 