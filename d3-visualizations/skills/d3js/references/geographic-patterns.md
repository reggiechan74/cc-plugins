# Geographic Patterns — D3.js v7

Patterns for map visualizations including choropleth, projections, and geographic data handling.

---

## Geographic Data Formats

### GeoJSON

Standard format. Each feature has a `geometry` (coordinates) and `properties` (attributes).

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {"name": "California", "population": 39538223},
      "geometry": {"type": "MultiPolygon", "coordinates": [...]}
    }
  ]
}
```

### TopoJSON

Compressed format — much smaller file sizes. Must convert to GeoJSON before rendering.

```javascript
import {feature, mesh} from "https://cdn.jsdelivr.net/npm/topojson-client@3/+esm";

// Convert TopoJSON to GeoJSON features
const countries = feature(topology, topology.objects.countries);

// Get mesh for borders (shared edges drawn once)
const borders = mesh(topology, topology.objects.countries, (a, b) => a !== b);
```

### Common Data Sources

- **World**: `https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json` (TopoJSON)
- **US States**: `https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json` (TopoJSON)
- **US Counties**: `https://cdn.jsdelivr.net/npm/us-atlas@3/counties-10m.json` (TopoJSON)

---

## Projections

Map projections transform spherical coordinates to 2D screen coordinates.

```javascript
const projection = d3.geoMercator()
  .fitSize([width, height], geojson);   // auto-fit to container

const path = d3.geoPath(projection);    // path generator
```

### Common Projections

| Projection | Use Case |
|------------|----------|
| `d3.geoMercator()` | Web maps, familiar look, distorts area at poles |
| `d3.geoAlbersUsa()` | US maps (includes Alaska/Hawaii insets) |
| `d3.geoEquirectangular()` | Simple lat/lon grid, good for world overview |
| `d3.geoOrthographic()` | Globe view, shows one hemisphere |
| `d3.geoNaturalEarth1()` | World maps with natural look, good area preservation |
| `d3.geoConicEqualArea()` | Regional maps, preserves area |

### Fitting Projections

```javascript
// Fit to specific feature collection
projection.fitSize([width, height], featureCollection);

// Fit with padding
projection.fitExtent([[20, 20], [width - 20, height - 20]], featureCollection);

// Manual configuration
d3.geoMercator()
  .center([0, 40])
  .scale(150)
  .translate([width / 2, height / 2]);
```

---

## Choropleth Map

Best for showing quantitative values across geographic regions.

```javascript
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import * as topojson from "https://cdn.jsdelivr.net/npm/topojson-client@3/+esm";

// Load data
const us = await d3.json("https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json");
const states = topojson.feature(us, us.objects.states);
const stateBorders = topojson.mesh(us, us.objects.states, (a, b) => a !== b);

// Create a lookup from state ID to value
const dataMap = new Map(data.map(d => [d.id, d.value]));

// Projection + path
const projection = d3.geoAlbersUsa().fitSize([width, height], states);
const path = d3.geoPath(projection);

// Color scale
const color = d3.scaleSequential()
  .domain(d3.extent(data, d => d.value))
  .interpolator(d3.interpolateBlues);

// Draw states
svg.selectAll("path.state")
  .data(states.features)
  .join("path")
  .attr("class", "state")
  .attr("d", path)
  .attr("fill", d => {
    const val = dataMap.get(d.id);
    return val != null ? color(val) : "#eee";
  })
  .attr("stroke", "none");

// State borders
svg.append("path")
  .datum(stateBorders)
  .attr("fill", "none")
  .attr("stroke", "white")
  .attr("stroke-width", 0.5)
  .attr("d", path);
```

### Color Legend for Choropleth

```javascript
const legendWidth = 260;
const legendHeight = 10;

const legendScale = d3.scaleLinear()
  .domain(color.domain())
  .range([0, legendWidth]);

const legendAxis = d3.axisBottom(legendScale)
  .ticks(5)
  .tickSize(legendHeight + 4);

const defs = svg.append("defs");
const gradient = defs.append("linearGradient")
  .attr("id", "legend-gradient");

gradient.selectAll("stop")
  .data(d3.range(0, 1.01, 0.01))
  .join("stop")
  .attr("offset", d => `${d * 100}%`)
  .attr("stop-color", d => color(legendScale.invert(d * legendWidth)));

const legend = svg.append("g")
  .attr("transform", `translate(${width - legendWidth - 30},${height - 40})`);

legend.append("rect")
  .attr("width", legendWidth)
  .attr("height", legendHeight)
  .attr("fill", "url(#legend-gradient)");

legend.append("g")
  .call(legendAxis)
  .select(".domain").remove();
```

---

## World Map

```javascript
const world = await d3.json("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json");
const countries = topojson.feature(world, world.objects.countries);
const borders = topojson.mesh(world, world.objects.countries, (a, b) => a !== b);

const projection = d3.geoNaturalEarth1()
  .fitSize([width, height], {type: "Sphere"});

const path = d3.geoPath(projection);

// Sphere outline
svg.append("path")
  .datum({type: "Sphere"})
  .attr("d", path)
  .attr("fill", "#f0f4f8")
  .attr("stroke", "#ccc");

// Graticule (grid lines)
svg.append("path")
  .datum(d3.geoGraticule()())
  .attr("d", path)
  .attr("fill", "none")
  .attr("stroke", "#e0e0e0")
  .attr("stroke-width", 0.5);

// Countries
svg.selectAll("path.country")
  .data(countries.features)
  .join("path")
  .attr("class", "country")
  .attr("d", path)
  .attr("fill", "#ddd")
  .attr("stroke", "white")
  .attr("stroke-width", 0.3);
```

---

## Bubble Map / Spike Map

Overlay sized markers on a geographic base.

```javascript
// After drawing base map...
// Data: [{lat, lon, value, label}]

svg.selectAll("circle.bubble")
  .data(bubbleData)
  .join("circle")
  .attr("class", "bubble")
  .attr("cx", d => projection([d.lon, d.lat])[0])
  .attr("cy", d => projection([d.lon, d.lat])[1])
  .attr("r", d => radiusScale(d.value))
  .attr("fill", "steelblue")
  .attr("fill-opacity", 0.5)
  .attr("stroke", "steelblue")
  .attr("stroke-width", 1);
```

### Spike Map

```javascript
const spikeHeight = d3.scaleLinear()
  .domain([0, d3.max(data, d => d.value)])
  .range([0, 50]);

svg.selectAll("line.spike")
  .data(data)
  .join("line")
  .attr("class", "spike")
  .attr("x1", d => projection([d.lon, d.lat])[0])
  .attr("y1", d => projection([d.lon, d.lat])[1])
  .attr("x2", d => projection([d.lon, d.lat])[0])
  .attr("y2", d => projection([d.lon, d.lat])[1] - spikeHeight(d.value))
  .attr("stroke", "steelblue")
  .attr("stroke-width", 1.5)
  .attr("stroke-opacity", 0.6);
```

---

## Interactive Features

### Zoom + Pan on Map

```javascript
const zoom = d3.zoom()
  .scaleExtent([1, 8])
  .on("zoom", (event) => {
    svg.selectAll("path").attr("transform", event.transform);
    svg.selectAll("circle").attr("transform", event.transform);
  });

svg.call(zoom);
```

### Tooltip on Hover

```javascript
svg.selectAll("path.state")
  .on("mouseover", (event, d) => {
    d3.select(event.currentTarget).attr("stroke", "#333").attr("stroke-width", 1.5);
    tooltip.style("opacity", 1)
      .html(`<strong>${d.properties.name}</strong><br/>Value: ${dataMap.get(d.id)}`);
  })
  .on("mousemove", (event) => {
    tooltip.style("left", (event.pageX + 10) + "px").style("top", (event.pageY - 20) + "px");
  })
  .on("mouseout", (event) => {
    d3.select(event.currentTarget).attr("stroke", "white").attr("stroke-width", 0.5);
    tooltip.style("opacity", 0);
  });
```

---

## Sample Geographic Data

For quick prototyping without loading external files, use inline GeoJSON. For real maps, load from CDN:

```javascript
// US states (TopoJSON, ~100KB)
const us = await d3.json("https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json");

// World countries (TopoJSON, ~200KB)
const world = await d3.json("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json");

// Higher resolution
const usHigh = await d3.json("https://cdn.jsdelivr.net/npm/us-atlas@3/states-albers-10m.json");
```

### Mock State Data

```javascript
const stateData = [
  {id: "06", name: "California", value: 39538223},
  {id: "48", name: "Texas", value: 29145505},
  {id: "12", name: "Florida", value: 21538187},
  {id: "36", name: "New York", value: 20201249},
  {id: "17", name: "Illinois", value: 12812508},
  // ...
];
```

Note: State IDs are FIPS codes (strings). Country IDs in world-atlas are ISO 3166-1 numeric codes.
