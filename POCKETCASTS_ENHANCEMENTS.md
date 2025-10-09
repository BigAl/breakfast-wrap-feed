# PocketCasts Enhancements

This feed includes several optimizations specifically for PocketCasts users, leveraging modern podcast standards.

## ✨ Features Added

### 1. **Podcast GUID (Podcasting 2.0)**
- **What it is**: A permanent unique identifier for the podcast
- **Benefits**:
  - PocketCasts can track the podcast even if the feed URL changes
  - Required for advanced Podcasting 2.0 features
  - Ensures consistent podcast identity across platforms
- **Our GUID**: `f95d7b89-e1ee-554c-be7f-f126f0b92dae`
- **Standard**: Generated using UUIDv5 as per [Podcasting 2.0 spec](https://github.com/Podcastindex-org/podcast-namespace/blob/main/docs/1.0.md#guid)

### 2. **WebSub (PubSubHubbub) Support**
- **What it is**: Instant notification protocol for new episodes
- **Benefits**:
  - Episodes appear in PocketCasts **immediately** after publication (instead of waiting 20+ minutes for polling)
  - Reduces server load and bandwidth
  - Better user experience with near-instant episode availability
- **How it works**:
  - Our feed includes `<atom:link rel="hub">` pointing to Google's WebSub hub
  - When GitHub Actions updates the feed, the hub can be notified
  - PocketCasts receives instant notification instead of polling every 20 minutes
- **Hub**: Using Google's public WebSub hub at `https://pubsubhubbub.appspot.com`

### 3. **Atom Self-Reference**
- **What it is**: Feed includes a link to itself
- **Benefits**:
  - Required for WebSub to function properly
  - Helps podcast apps verify they're using the canonical feed URL
  - Improves feed autodiscovery

## 🔧 Technical Details

### Feed Structure
```xml
<rss version="2.0"
     xmlns:podcast="https://podcastindex.org/namespace/1.0"
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <!-- Standard metadata -->
    <title>Radio National Breakfast - Breakfast Wrap</title>

    <!-- Atom self-reference (required for WebSub) -->
    <atom:link href="https://bigal.github.io/breakfast-wrap-feed/breakfast-wrap.xml"
               rel="self"
               type="application/rss+xml"/>

    <!-- WebSub hub -->
    <atom:link href="https://pubsubhubbub.appspot.com"
               rel="hub"/>

    <!-- Podcast GUID (Podcasting 2.0) -->
    <podcast:guid>f95d7b89-e1ee-554c-be7f-f126f0b92dae</podcast:guid>

    <!-- Episodes... -->
  </channel>
</rss>
```

### GUID Generation
The podcast GUID is generated using Python's `uuid` library:

```python
import uuid

# Official podcast namespace UUID
PODCAST_NAMESPACE = uuid.UUID('ead4c236-bf58-58c6-a2c6-a6b28d128cb6')

# Normalize feed URL (strip protocol and trailing slashes)
normalized_url = "bigal.github.io/breakfast-wrap-feed/breakfast-wrap.xml"

# Generate UUIDv5
guid = str(uuid.uuid5(PODCAST_NAMESPACE, normalized_url))
# Result: f95d7b89-e1ee-554c-be7f-f126f0b92dae
```

This ensures the GUID is:
- Deterministic (same feed URL always generates the same GUID)
- Unique globally
- Compatible with the Podcasting 2.0 specification

## 📊 Expected Impact

### For PocketCasts Users
- **Faster episode discovery**: Episodes appear within minutes instead of up to 20 minutes
- **Reliable feed tracking**: Even if we change hosting, PocketCasts maintains subscription
- **Future-proof**: Ready for upcoming Podcasting 2.0 features PocketCasts may adopt

### Backward Compatibility
All enhancements are **100% backward compatible**:
- Non-PocketCasts apps ignore the new tags
- Standard RSS/iTunes tags remain unchanged
- No breaking changes for existing subscribers

## 📚 References

- [Podcasting 2.0 Namespace Specification](https://github.com/Podcastindex-org/podcast-namespace)
- [PocketCasts Feed Parsing Documentation](https://support.pocketcasts.com/knowledge-base/podcast-parsing/)
- [WebSub Specification](https://www.w3.org/TR/websub/)
- [Google PubSubHubbub Hub](https://pubsubhubbub.appspot.com/)

## 🚀 Future Enhancements

Other Podcasting 2.0 features we could consider:
- **podcast:funding** - Add donation/support links (if ABC allows)
- **podcast:chapters** - Episode chapter markers (would need to generate from ABC data)
- **podcast:transcript** - Episode transcripts (if ABC provides them)
- **Podping** - Alternative to WebSub using blockchain (more advanced)

These would further enhance the PocketCasts experience while maintaining compatibility with all podcast apps.
