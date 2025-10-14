# Static Data Files

This directory contains minified JSON data files for geographical and language information used throughout the application.

## Files Overview

| File | Size | Description | Location |
|------|------|-------------|----------|
| `citiesminified.json` | ~34MB | Complete list of cities worldwide with country/state associations | `/public/data/` (dynamically loaded) |
| `statesminified.json` | ~591KB | List of states/provinces with country associations | `/public/data/` (dynamically loaded) |
| `countriesminified.json` | ~116KB | List of countries with ISO codes and basic information | `/src/static-data/` (bundled) |
| `languagesminified.json` | ~14KB | List of languages with ISO codes | `/src/static-data/` (bundled) |
| `regionsminified.json` | ~419B | List of geographical regions | `/src/static-data/` (bundled) |

## Usage

These files are designed to be:
- **Minified**: Optimized for production use with reduced file sizes
- **Static**: Rarely changing data that can be cached effectively
- **Comprehensive**: Complete datasets for global applications

## Import Examples

### Server-side (Next.js API routes, Server Components)
```typescript
import countries from '@/static-data/countriesminified.json'
import states from '@/static-data/statesminified.json'
import cities from '@/static-data/citiesminified.json'
```

### Client-side (Dynamic loading for large files)
```typescript
// Large files are loaded dynamically from public folder
const loadStates = async () => {
  const response = await fetch('/data/statesminified.json')
  return response.json()
}

const loadCities = async () => {
  const response = await fetch('/data/citiesminified.json')
  return response.json()
}
```

### File Locations
- **Small files** (countries, languages, regions): Located in `/src/static-data/` and bundled (~130KB total)
- **Large files** (states, cities): Located in `/public/data/` and loaded dynamically to avoid bundle bloat

## Performance Considerations

- **Cities file (34MB)**: Consider lazy loading or pagination for large datasets
- **Countries/States**: Can be loaded immediately as they're relatively small
- **Caching**: These files rarely change, so implement proper caching strategies

## Data Structure

Each file follows a consistent JSON structure optimized for:
- Fast lookups by ID or code
- Efficient filtering and searching
- Minimal memory footprint

## Updates

When updating these files:
1. Ensure JSON validity
2. Test import/usage in development
3. Consider impact on bundle size
4. Update this README if structure changes
