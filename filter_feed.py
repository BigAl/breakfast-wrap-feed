#!/usr/bin/env python3
"""
Filter ABC News Daily podcast feed for Breakfast Wrap episodes only.
"""

import feedparser
import requests
from datetime import datetime
from xml.etree import ElementTree as ET
from xml.dom import minidom

# Configuration
SOURCE_FEED_URL = "https://www.abc.net.au/feeds/2890360/podcast.xml"
OUTPUT_FILE = "breakfast-wrap.xml"
FILTER_KEYWORD = "Breakfast Wrap"
MAX_EPISODES = 50

def fetch_feed(url):
    """Fetch the RSS feed from URL."""
    print(f"Fetching feed from {url}...")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return feedparser.parse(response.content)

def filter_entries(feed, keyword):
    """Filter entries that contain keyword in title."""
    filtered = []
    for entry in feed.entries:
        if keyword.lower() in entry.get('title', '').lower():
            filtered.append(entry)
            print(f"✓ Found: {entry.title}")

    print(f"\nFiltered {len(filtered)} episodes out of {len(feed.entries)} total")
    return filtered[:MAX_EPISODES]

def create_rss_feed(original_feed, filtered_entries):
    """Create new RSS feed XML with filtered entries."""

    # Create RSS root
    rss = ET.Element('rss', {
        'version': '2.0',
        'xmlns:itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
        'xmlns:content': 'http://purl.org/rss/1.0/modules/content/',
        'xmlns:atom': 'http://www.w3.org/2005/Atom'
    })

    channel = ET.SubElement(rss, 'channel')

    # Channel metadata
    ET.SubElement(channel, 'title').text = f"{original_feed.feed.get('title', 'ABC News Daily')} - Breakfast Wrap"
    ET.SubElement(channel, 'description').text = f"Filtered feed containing only Breakfast Wrap episodes from {original_feed.feed.get('title', 'ABC News Daily')}"
    ET.SubElement(channel, 'link').text = original_feed.feed.get('link', 'https://www.abc.net.au/newsradio/programs/newsradio-news-daily/')
    ET.SubElement(channel, 'language').text = original_feed.feed.get('language', 'en')
    ET.SubElement(channel, 'lastBuildDate').text = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

    # Use custom podcast artwork
    image = ET.SubElement(channel, 'image')
    ET.SubElement(image, 'url').text = 'https://bigal.github.io/breakfast-wrap-feed/podcast-artwork.jpg'
    ET.SubElement(image, 'title').text = f"{original_feed.feed.get('title', 'ABC News Daily')} - Breakfast Wrap"
    ET.SubElement(image, 'link').text = 'https://bigal.github.io/breakfast-wrap-feed/'

    # iTunes/Podcast-specific metadata
    ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}image', {
        'href': 'https://bigal.github.io/breakfast-wrap-feed/podcast-artwork.jpg'
    })
    ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}author').text = 'ABC Radio National'
    ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}category', {
        'text': 'News'
    })
    ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit').text = 'false'
    ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}owner').text = ''
    owner = ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}owner')
    ET.SubElement(owner, '{http://www.itunes.com/dtds/podcast-1.0.dtd}name').text = 'ABC Radio National'
    ET.SubElement(owner, '{http://www.itunes.com/dtds/podcast-1.0.dtd}email').text = 'podcasts@abc.net.au'

    # Add filtered items
    for entry in filtered_entries:
        item = ET.SubElement(channel, 'item')

        # Basic fields
        ET.SubElement(item, 'title').text = entry.get('title', '')
        ET.SubElement(item, 'description').text = entry.get('summary', entry.get('description', ''))
        ET.SubElement(item, 'link').text = entry.get('link', '')
        ET.SubElement(item, 'guid', {'isPermaLink': 'false'}).text = entry.get('id', entry.get('link', ''))

        # Publication date
        if hasattr(entry, 'published'):
            ET.SubElement(item, 'pubDate').text = entry.published

        # Enclosure (audio file) - this points to ABC's original media
        if hasattr(entry, 'enclosures') and entry.enclosures:
            enclosure = entry.enclosures[0]
            ET.SubElement(item, 'enclosure', {
                'url': enclosure.get('href', ''),
                'length': enclosure.get('length', '0'),
                'type': enclosure.get('type', 'audio/mpeg')
            })

        # iTunes specific fields
        if hasattr(entry, 'itunes_duration'):
            ET.SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}duration').text = entry.itunes_duration
        if hasattr(entry, 'itunes_author'):
            ET.SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}author').text = entry.itunes_author

    return rss

def prettify_xml(elem):
    """Return a pretty-printed XML string."""
    rough_string = ET.tostring(elem, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')

def main():
    """Main execution."""
    try:
        # Fetch original feed
        feed = fetch_feed(SOURCE_FEED_URL)

        # Filter for Breakfast Wrap episodes
        filtered = filter_entries(feed, FILTER_KEYWORD)

        if not filtered:
            print("⚠️  No episodes found matching filter criteria")
            return

        # Create new RSS feed
        rss_xml = create_rss_feed(feed, filtered)

        # Write to file
        xml_string = prettify_xml(rss_xml)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(xml_string)

        print(f"\n✅ Successfully created {OUTPUT_FILE} with {len(filtered)} episodes")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()
