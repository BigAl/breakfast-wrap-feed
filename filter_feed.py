#!/usr/bin/env python3
"""
Filter ABC News Daily podcast feed for Breakfast Wrap episodes only.
"""

import feedparser
import requests
import os
import sys
import uuid
from datetime import datetime, timezone
from xml.etree import ElementTree as ET
from xml.dom import minidom

# Configuration
SOURCE_FEED_URL = "https://www.abc.net.au/feeds/2890360/podcast.xml"
OUTPUT_FILE = "breakfast-wrap.xml"
BACKUP_FILE = f"{OUTPUT_FILE}.backup"
FILTER_KEYWORD = "Breakfast Wrap"
MAX_EPISODES = 50
FEED_URL = "https://bigal.github.io/breakfast-wrap-feed/breakfast-wrap.xml"
WEBSUB_HUB = "https://pubsubhubbub.appspot.com"  # Google's WebSub hub

def fetch_feed(url, retries=3):
    """Fetch the RSS feed from URL with retries."""
    print(f"Fetching feed from {url}...")

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            feed = feedparser.parse(response.content)

            # Check if feed is valid
            if hasattr(feed, 'bozo') and feed.bozo:
                print(f"⚠️  Warning: Feed has parsing errors: {feed.bozo_exception}")

            if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                raise ValueError("Feed contains no entries")

            print(f"✓ Successfully fetched feed with {len(feed.entries)} total episodes")
            return feed

        except requests.exceptions.Timeout:
            print(f"⏱️  Attempt {attempt}/{retries}: Connection timeout")
            if attempt < retries:
                print(f"   Retrying...")
            else:
                raise RuntimeError(f"Failed to fetch feed after {retries} attempts: Connection timeout")

        except requests.exceptions.ConnectionError as e:
            print(f"🔌 Attempt {attempt}/{retries}: Connection error - {e}")
            if attempt < retries:
                print(f"   Retrying...")
            else:
                raise RuntimeError(f"Failed to fetch feed after {retries} attempts: Cannot connect to ABC servers")

        except requests.exceptions.HTTPError as e:
            print(f"❌ Attempt {attempt}/{retries}: HTTP error {e.response.status_code}")
            if e.response.status_code >= 500:
                # Server error, retry
                if attempt < retries:
                    print(f"   Server error, retrying...")
                else:
                    raise RuntimeError(f"ABC feed server error: {e.response.status_code}. The ABC feed may be temporarily down.")
            else:
                # Client error (404, 403, etc), don't retry
                raise RuntimeError(f"Feed fetch failed: HTTP {e.response.status_code}. The feed URL may have changed.")

        except Exception as e:
            print(f"❌ Attempt {attempt}/{retries}: Unexpected error - {e}")
            if attempt < retries:
                print(f"   Retrying...")
            else:
                raise

def filter_entries(feed, keyword):
    """Filter entries that contain keyword in title or summary."""
    filtered = []
    for entry in feed.entries:
        title = entry.get('title', '').lower()
        summary = entry.get('summary', '').lower()

        # Check for keyword in title or summary
        if keyword.lower() in title or keyword.lower() in summary:
            # If it's the main "Breakfast" episode which now contains the wrap, rename it for consistency
            if title.startswith('breakfast:'):
                entry.title = 'Breakfast Wrap:' + entry.title.split(':', 1)[1]

            filtered.append(entry)
            print(f"✓ Found: {entry.title}")

    print(f"\nFiltered {len(filtered)} episodes out of {len(feed.entries)} total")
    return filtered[:MAX_EPISODES]

def generate_podcast_guid(feed_url):
    """Generate a UUIDv5 for the podcast using the Podcast GUID namespace."""
    # Official podcast namespace UUID as per https://github.com/Podcastindex-org/podcast-namespace
    PODCAST_NAMESPACE = uuid.UUID('ead4c236-bf58-58c6-a2c6-a6b28d128cb6')

    # Strip protocol and trailing slashes from feed URL as per spec
    normalized_url = feed_url.replace('https://', '').replace('http://', '').rstrip('/')

    # Generate UUIDv5
    return str(uuid.uuid5(PODCAST_NAMESPACE, normalized_url))

def create_rss_feed(original_feed, filtered_entries):
    """Create new RSS feed XML with filtered entries."""

    # Register namespaces BEFORE creating elements to avoid ns0, ns1, ns2 prefixes
    ET.register_namespace('itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')
    ET.register_namespace('content', 'http://purl.org/rss/1.0/modules/content/')
    ET.register_namespace('atom', 'http://www.w3.org/2005/Atom')
    ET.register_namespace('podcast', 'https://podcastindex.org/namespace/1.0')

    # Create RSS root - namespaces will be added automatically when we use them
    rss = ET.Element('rss', {'version': '2.0'})

    channel = ET.SubElement(rss, 'channel')

    # Channel metadata
    ET.SubElement(channel, 'title').text = f"{original_feed.feed.get('title', 'ABC News Daily')} - Breakfast Wrap"
    ET.SubElement(channel, 'description').text = f"Filtered feed containing only Breakfast Wrap episodes from {original_feed.feed.get('title', 'ABC News Daily')}"
    ET.SubElement(channel, 'link').text = original_feed.feed.get('link', 'https://www.abc.net.au/newsradio/programs/newsradio-news-daily/')
    ET.SubElement(channel, 'language').text = original_feed.feed.get('language', 'en')
    ET.SubElement(channel, 'lastBuildDate').text = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

    # Atom self-reference (required for WebSub)
    ET.SubElement(channel, '{http://www.w3.org/2005/Atom}link', {
        'href': FEED_URL,
        'rel': 'self',
        'type': 'application/rss+xml'
    })

    # WebSub hub for instant episode notifications
    ET.SubElement(channel, '{http://www.w3.org/2005/Atom}link', {
        'href': WEBSUB_HUB,
        'rel': 'hub'
    })

    # Podcast GUID (Podcasting 2.0) - permanent identifier
    podcast_guid = generate_podcast_guid(FEED_URL)
    ET.SubElement(channel, '{https://podcastindex.org/namespace/1.0}guid').text = podcast_guid
    print(f"📋 Generated podcast GUID: {podcast_guid}")

    # Use custom podcast artwork
    image = ET.SubElement(channel, 'image')
    ET.SubElement(image, 'url').text = 'https://bigal.github.io/breakfast-wrap-feed/podcast-artwork.jpg'
    ET.SubElement(image, 'title').text = f"{original_feed.feed.get('title', 'ABC News Daily')} - Breakfast Wrap"
    ET.SubElement(image, 'link').text = original_feed.feed.get('link', 'https://www.abc.net.au/newsradio/programs/newsradio-news-daily/')

    # iTunes/Podcast-specific metadata
    ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}image', {
        'href': 'https://bigal.github.io/breakfast-wrap-feed/podcast-artwork.jpg'
    })
    ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}author').text = 'ABC Radio National'
    ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}category', {
        'text': 'News'
    })
    ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit').text = 'false'

    # iTunes owner (only one, with required name and email)
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

def backup_existing_feed():
    """Create a backup of the existing feed if it exists."""
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as src:
                content = src.read()
            with open(BACKUP_FILE, 'w', encoding='utf-8') as dst:
                dst.write(content)
            print(f"📦 Backed up existing feed to {BACKUP_FILE}")
            return True
        except Exception as e:
            print(f"⚠️  Could not create backup: {e}")
            return False
    return False

def restore_from_backup():
    """Restore feed from backup if available."""
    if os.path.exists(BACKUP_FILE):
        try:
            with open(BACKUP_FILE, 'r', encoding='utf-8') as src:
                content = src.read()
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as dst:
                dst.write(content)
            print(f"♻️  Restored feed from backup")
            return True
        except Exception as e:
            print(f"❌ Failed to restore from backup: {e}")
            return False
    return False

def get_existing_guids(filename):
    """Parse an existing feed file and return a set of entry GUIDs."""
    if not os.path.exists(filename):
        return set()
    
    try:
        # Use feedparser to read the local file
        existing_feed = feedparser.parse(filename)
        if existing_feed.bozo:
            print(f"⚠️  Warning: Existing feed '{filename}' has parsing errors. Will rebuild.")
            return set()

        # Use entry 'id' as the unique identifier (GUID)
        return {entry.get('id', entry.get('link', '')) for entry in existing_feed.entries}
    except Exception as e:
        print(f"⚠️  Could not parse existing feed file: {e}. Will rebuild.")
        return set()


def main():
    """Main execution."""
    backup_created = backup_existing_feed()

    try:
        # Get GUIDs from the existing feed file before fetching the new one
        existing_guids = get_existing_guids(OUTPUT_FILE)
        if existing_guids:
            print(f"Found {len(existing_guids)} episodes in the current feed file.")

        # Fetch original feed
        feed = fetch_feed(SOURCE_FEED_URL)

        # Filter for Breakfast Wrap episodes
        filtered = filter_entries(feed, FILTER_KEYWORD)

        if not filtered:
            print("⚠️  No episodes found matching filter criteria")
            if backup_created:
                print("   Keeping existing feed unchanged")
                restore_from_backup()
            # Exit gracefully, but with an error code if no backup exists, to trigger notifications
            sys.exit(1 if not backup_created else 0)

        # Get GUIDs from the newly filtered entries
        new_guids = {entry.get('id', entry.get('link', '')) for entry in filtered}

        # Compare the set of existing GUIDs with the new ones
        if existing_guids == new_guids:
            print("\n✅ Feed is already up-to-date. No changes needed.")
            # Clean up backup since the run was successful and no changes were made
            if os.path.exists(BACKUP_FILE):
                os.remove(BACKUP_FILE)
            return # Exit gracefully

        print("\n✨ Feed content has changed. Rebuilding file...")
        # Create new RSS feed
        rss_xml = create_rss_feed(feed, filtered)

        # Write to file
        xml_string = prettify_xml(rss_xml)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(xml_string)

        print(f"\n✅ Successfully created {OUTPUT_FILE} with {len(filtered)} episodes")

        # Clean up backup on success
        if os.path.exists(BACKUP_FILE):
            os.remove(BACKUP_FILE)

    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        print(f"\n📋 Error Details:")
        print(f"   Feed URL: {SOURCE_FEED_URL}")
        print(f"   Filter keyword: {FILTER_KEYWORD}")

        if backup_created:
            print(f"\n🔄 Attempting to restore previous feed...")
            if restore_from_backup():
                print(f"✓ Previous feed restored - subscribers will continue to see old episodes")
                print(f"⚠️  This error needs attention, but the feed remains functional")
                sys.exit(1)  # Exit with error so workflow notifications trigger
            else:
                print(f"❌ Could not restore backup - feed may be unavailable")
                raise
        else:
            print(f"\n⚠️  No backup available - cannot restore previous feed")
            raise

if __name__ == "__main__":
    main()
