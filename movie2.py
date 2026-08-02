import json
import requests
from datetime import datetime

def fetch_json_data(url):
    """Fetch JSON data from the URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def generate_stremio_m3u(json_data, output_file="movie.m3u"):
    """
    Generate a clean M3U playlist optimized for Stremio
    Follows standard M3U format that Stremio can parse
    """
    
    if not json_data or not json_data.get('success'):
        print("Invalid JSON data")
        return
    
    data = json_data.get('data', {})
    
    # Start with standard M3U header
    m3u_content = ['#EXTM3U']
    m3u_content.append(f'#PLAYLIST: Stremio Next - {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    m3u_content.append('')
    
    total_items = 0
    
    # Define categories and their display names
    categories = {
        'spotlight': 'Spotlight',
        'trending': 'Trending',
        'popularMovies': 'Popular Movies',
        'topMovies': 'Top Movies',
        'nowPlaying': 'Now Playing',
        'upcoming': 'Upcoming',
        'popularTv': 'Popular TV Shows',
        'topTv': 'Top TV Shows',
        'onTheAir': 'On The Air',
        'animeTv': 'Anime TV',
        'animeMovies': 'Anime Movies'
    }
    
    # Process each category
    for category_key, category_name in categories.items():
        if category_key in data and isinstance(data[category_key], list):
            items = data[category_key]
            
            # Add category header comment
            m3u_content.append(f'#CATEGORY: {category_name}')
            
            for item in items:
                if not isinstance(item, dict):
                    continue
                    
                total_items += 1
                
                # Extract item data
                title = item.get('title', 'Unknown')
                year = item.get('year', '')
                rating = item.get('rating', '')
                poster = item.get('poster', '')
                item_type = item.get('type', 'movie')
                item_id = item.get('id', '')
                date = item.get('date', '')
                overview = item.get('overview', '')
                original_title = item.get('originalTitle', title)
                lang = item.get('lang', 'en')
                
                # Build the display name with metadata
                display_title = title
                if year:
                    display_title += f" ({year})"
                if rating:
                    display_title += f" ★{rating}"
                
                # Create EXTINF line with tvg metadata
                extinf_parts = []
                
                # Add tvg-logo (poster)
                if poster:
                    poster_url = f"https://image.tmdb.org/t/p/w500{poster}"
                    extinf_parts.append(f'tvg-logo="{poster_url}"')
                
                # Add group title (category)
                extinf_parts.append(f'group-title="{category_name}"')
                
                # Add tvg-id (item ID)
                extinf_parts.append(f'tvg-id="{item_id}"')
                
                # Add tvg-name (original title)
                extinf_parts.append(f'tvg-name="{original_title}"')
                
                # Add tvg-year
                if year:
                    extinf_parts.append(f'tvg-year="{year}"')
                
                # Add tvg-language
                extinf_parts.append(f'tvg-language="{lang}"')
                
                # Build the EXTINF line
                extinf_line = '#EXTINF:-1'
                if extinf_parts:
                    extinf_line += ' ' + ' '.join(extinf_parts)
                extinf_line += f',{display_title}'
                
                m3u_content.append(extinf_line)
                
                # Add description as comment (optional but helpful)
                if overview:
                    m3u_content.append(f'#DESC: {overview[:200]}{"..." if len(overview) > 200 else ""}')
                
                # Generate stream URL for Stremio
                # This uses the Stremio API endpoint format
                stream_url = f"https://stremio-next.vercel.app/api/watch/{item_type}/{item_id}"
                m3u_content.append(stream_url)
                m3u_content.append('')  # Empty line between entries
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(m3u_content))
    
    print(f"✅ Stremio playlist generated: {output_file}")
    print(f"📊 Total items: {total_items}")
    print(f"📁 Categories included: {len([k for k in categories.keys() if k in data])}")
    
    return output_file

def generate_compact_m3u(json_data, output_file="movie_compact.m3u"):
    """
    Generate a compact M3U playlist with just essentials
    Best for performance and compatibility
    """
    
    if not json_data or not json_data.get('success'):
        print("Invalid JSON data")
        return
    
    data = json_data.get('data', {})
    
    m3u_content = ['#EXTM3U']
    m3u_content.append(f'#PLAYLIST: Stremio Next - {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    m3u_content.append('')
    
    total_items = 0
    
    # Process all items from all categories
    for category_key, items in data.items():
        if isinstance(items, list):
            for item in items:
                if not isinstance(item, dict):
                    continue
                
                total_items += 1
                
                title = item.get('title', 'Unknown')
                year = item.get('year', '')
                rating = item.get('rating', '')
                poster = item.get('poster', '')
                item_type = item.get('type', 'movie')
                item_id = item.get('id', '')
                
                # Build display title
                display_title = title
                if year:
                    display_title += f" ({year})"
                if rating:
                    display_title += f" [★{rating}]"
                
                # Create EXTINF with minimal metadata
                extinf_parts = []
                
                # Add poster if available
                if poster:
                    poster_url = f"https://image.tmdb.org/t/p/w200{poster}"
                    extinf_parts.append(f'tvg-logo="{poster_url}"')
                
                # Add type
                extinf_parts.append(f'tvg-type="{item_type}"')
                
                # Build EXTINF line
                extinf_line = '#EXTINF:-1'
                if extinf_parts:
                    extinf_line += ' ' + ' '.join(extinf_parts)
                extinf_line += f',{display_title}'
                
                m3u_content.append(extinf_line)
                
                # Stream URL
                stream_url = f"https://stremio-next.vercel.app/api/watch/{item_type}/{item_id}"
                m3u_content.append(stream_url)
                m3u_content.append('')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(m3u_content))
    
    print(f"✅ Compact playlist generated: {output_file}")
    print(f"📊 Total items: {total_items}")
    
    return output_file

def main():
    url = "https://stremio-next.vercel.app/api/home"
    
    print("🚀 Fetching data from Stremio Next...")
    json_data = fetch_json_data(url)
    
    if json_data:
        print("✅ Data fetched successfully!")
        print("")
        
        # Generate the best version for Stremio
        print("📝 Generating Stremio-optimized playlists...")
        print("-" * 50)
        
        # Full featured playlist with all metadata (output as movie.m3u)
        generate_stremio_m3u(json_data, "movie.m3u")
        print("")
        
        # Compact version for better performance
        generate_compact_m3u(json_data, "movie_compact.m3u")
        print("")
        
        print("=" * 50)
        print("✨ Playlist generation complete!")
        print("📁 Files created:")
        print("   • movie.m3u - Full version with all metadata (MAIN FILE)")
        print("   • movie_compact.m3u - Compact version for better performance")
        print("")
        print("🔧 To use in Stremio:")
        print("   1. Go to Stremio → Settings → Addons")
        print("   2. Click 'Install from URL'")
        print("   3. Enter the URL to your M3U file (or use the local file)")
        print("   4. Or use an IPTV addon with the M3U file")
        print("=" * 50)
    else:
        print("❌ Failed to fetch data. Please check your internet connection.")
        print("   You can also save the JSON locally and use it directly.")

if __name__ == "__main__":
    main()
