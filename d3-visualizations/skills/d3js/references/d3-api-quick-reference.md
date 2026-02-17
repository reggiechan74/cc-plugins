# D3.js v7 API Quick Reference

Module-by-module reference for D3.js v7. Import the full library or individual modules:

```javascript
// Full library
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";

// Individual module
import {scaleLinear} from "https://cdn.jsdelivr.net/npm/d3-scale@4/+esm";
```

---

## d3-selection — DOM Manipulation

```javascript
d3.select("selector")          // select first match
d3.selectAll("selector")       // select all matches
selection.select("child")      // select first child match
selection.selectAll("children") // select all child matches

// Modifying
selection.attr("name", value)
selection.style("prop", value)
selection.classed("name", bool)
selection.text(value)
selection.html(value)
selection.property("name", value)

// Adding/removing
selection.append("element")
selection.insert("element", "before")
selection.remove()
selection.raise()              // move to front
selection.lower()              // move to back

// Data join (v7 pattern)
selection.data(array, keyFn)
  .join("element")             // enter + update + exit in one call
  .join(
    enter => enter.append("element"),
    update => update,
    exit => exit.remove()
  )

// Events
selection.on("event", handler)   // click, mouseover, mouseout, etc.
d3.pointer(event, target)        // [x, y] coordinates
```

---

## d3-scale — Data → Visual Mapping

### Continuous Scales

```javascript
d3.scaleLinear()       // linear mapping
  .domain([min, max])
  .range([start, end])
  .nice()              // round domain to nice values
  .clamp(true)         // clamp output to range

d3.scaleTime()         // for Date objects
d3.scalePow().exponent(2)   // power scale
d3.scaleLog()          // logarithmic
d3.scaleSymlog()       // symlog (handles 0)
d3.scaleSqrt()         // square root (area encoding)
```

### Ordinal Scales

```javascript
d3.scaleBand()         // for bar charts (equal bands)
  .domain(categories)
  .range([0, width])
  .padding(0.2)        // gap between bands
  .bandwidth()         // computed band width

d3.scalePoint()        // for dot plots (point positions)
  .domain(categories)
  .range([0, width])
  .padding(0.5)

d3.scaleOrdinal()      // arbitrary mapping
  .domain(categories)
  .range(colors)
```

### Sequential & Diverging

```javascript
d3.scaleSequential(d3.interpolateBlues)
  .domain([min, max])

d3.scaleDiverging(d3.interpolateRdBu)
  .domain([min, mid, max])

d3.scaleQuantize()     // continuous → discrete bins
d3.scaleQuantile()     // by quantile
d3.scaleThreshold()    // explicit thresholds
```

---

## d3-axis — Axes

```javascript
d3.axisBottom(scale)   // ticks below
d3.axisTop(scale)      // ticks above
d3.axisLeft(scale)     // ticks left
d3.axisRight(scale)    // ticks right

// Configuration
axis.ticks(count)
axis.tickValues([...])
axis.tickFormat(d3.format(",.0f"))
axis.tickSize(length)
axis.tickSizeInner(length)
axis.tickSizeOuter(length)
axis.tickPadding(pixels)

// Render
svg.append("g")
  .attr("transform", `translate(0,${height})`)
  .call(d3.axisBottom(x));
```

---

## d3-shape — Lines, Areas, Arcs

### Lines & Areas

```javascript
d3.line()
  .x(d => xScale(d.x))
  .y(d => yScale(d.y))
  .defined(d => d.y != null)   // skip missing data
  .curve(d3.curveMonotoneX)    // curve interpolation

d3.area()
  .x(d => xScale(d.x))
  .y0(height)                  // baseline
  .y1(d => yScale(d.y))
  .curve(d3.curveMonotoneX)
```

**Curve types:** `d3.curveLinear`, `d3.curveMonotoneX`, `d3.curveBasis`, `d3.curveCardinal`, `d3.curveCatmullRom`, `d3.curveStep`, `d3.curveNatural`, `d3.curveBumpX`

### Arcs & Pies

```javascript
d3.arc()
  .innerRadius(r1)
  .outerRadius(r2)
  .startAngle(angle)
  .endAngle(angle)
  .padAngle(pad)
  .cornerRadius(r)

d3.pie()
  .value(d => d.value)
  .sort(null)                  // preserve data order
  .padAngle(0.02)
```

### Symbols

```javascript
d3.symbol()
  .type(d3.symbolCircle)
  .size(64)

// Types: symbolCircle, symbolCross, symbolDiamond, symbolSquare,
//        symbolStar, symbolTriangle, symbolWye
```

### Stack

```javascript
d3.stack()
  .keys(["a", "b", "c"])
  .order(d3.stackOrderNone)
  .offset(d3.stackOffsetNone)     // stacked
  // d3.stackOffsetExpand           // normalized (0-1)
  // d3.stackOffsetWiggle           // streamgraph
```

---

## d3-hierarchy — Trees & Layouts

```javascript
d3.hierarchy(data)              // create hierarchy from nested data
  .sum(d => d.value)
  .sort((a, b) => b.value - a.value)
  .descendants()                // all nodes
  .leaves()                     // leaf nodes
  .links()                      // parent-child links
  .ancestors()                  // path to root

d3.stratify()                   // hierarchy from flat data
  .id(d => d.id)
  .parentId(d => d.parentId)

// Layouts
d3.tree().size([w, h])          // tidy tree
d3.cluster().size([w, h])       // dendrogram (aligned leaves)
d3.treemap().size([w, h])       // treemap
  .tile(d3.treemapSquarify)
  .padding(2)
d3.pack().size([w, h])          // circle packing
  .padding(3)
d3.partition().size([w, h])     // sunburst/icicle
```

---

## d3-force — Force Simulation

```javascript
d3.forceSimulation(nodes)
  .force("link", d3.forceLink(links).id(d => d.id))
  .force("charge", d3.forceManyBody().strength(-200))
  .force("center", d3.forceCenter(w/2, h/2))
  .force("collision", d3.forceCollide().radius(r))
  .force("x", d3.forceX(targetX).strength(0.1))
  .force("y", d3.forceY(targetY).strength(0.1))
  .on("tick", tickHandler)
  .alpha(1)                    // initial energy
  .alphaDecay(0.02)           // cooling rate
  .alphaTarget(0)             // resting state
  .restart()
  .stop()
```

---

## d3-geo — Geographic

```javascript
// Projections
d3.geoMercator()
d3.geoAlbersUsa()
d3.geoNaturalEarth1()
d3.geoOrthographic()
d3.geoEquirectangular()

// Configuration
projection.center([lon, lat])
projection.scale(value)
projection.translate([x, y])
projection.rotate([lambda, phi, gamma])
projection.fitSize([w, h], geojson)
projection.fitExtent([[x0,y0],[x1,y1]], geojson)

// Path generator
d3.geoPath(projection)

// Utilities
d3.geoGraticule()()            // grid lines
d3.geoGraticule10()            // 10-degree grid
d3.geoCentroid(feature)        // geographic center
d3.geoArea(feature)            // spherical area
d3.geoDistance([lon1,lat1],[lon2,lat2])  // great-circle distance
```

---

## d3-transition — Animation

```javascript
selection.transition()
  .duration(750)               // milliseconds
  .delay(200)                  // start delay
  .delay((d, i) => i * 50)    // staggered delay
  .ease(d3.easeCubicInOut)     // easing function
  .attr("name", value)        // animate attribute
  .style("prop", value)       // animate style
  .attrTween("d", tweenFn)    // custom interpolation
  .on("start", fn)
  .on("end", fn)
  .transition()                // chain another transition
```

**Easing:** `d3.easeLinear`, `d3.easeCubicInOut`, `d3.easeBounce`, `d3.easeElastic`, `d3.easeBack`, `d3.easeCircle`, `d3.easePoly`

---

## d3-zoom — Pan & Zoom

```javascript
d3.zoom()
  .scaleExtent([min, max])
  .translateExtent([[x0,y0],[x1,y1]])
  .on("zoom", ({transform}) => {
    g.attr("transform", transform);
    // or: transform.rescaleX(x), transform.rescaleY(y)
  })

d3.zoomIdentity                // reset transform
  .translate(x, y)
  .scale(k)
```

---

## d3-brush — Selection

```javascript
d3.brush()                     // 2D selection
d3.brushX()                    // horizontal only
d3.brushY()                    // vertical only
  .extent([[x0,y0],[x1,y1]])
  .on("start brush end", handler)

// In handler:
event.selection                // [[x0,y0],[x1,y1]] or [x0,x1]
```

---

## d3-drag — Dragging

```javascript
d3.drag()
  .on("start", (event, d) => {})
  .on("drag", (event, d) => {
    // event.x, event.y = current position
    // event.dx, event.dy = delta
  })
  .on("end", (event, d) => {})
```

---

## d3-fetch — Data Loading

```javascript
d3.csv("file.csv")             // returns array of objects
d3.tsv("file.tsv")
d3.json("file.json")
d3.text("file.txt")
d3.xml("file.xml")
d3.image("file.png")

// With type coercion
d3.csv("file.csv", d => ({
  date: new Date(d.date),
  value: +d.value
}))
```

---

## d3-array — Data Utilities

```javascript
d3.min(array, accessor)
d3.max(array, accessor)
d3.extent(array, accessor)     // [min, max]
d3.sum(array, accessor)
d3.mean(array, accessor)
d3.median(array, accessor)
d3.deviation(array, accessor)  // standard deviation
d3.quantile(sorted, p)

d3.range(start, stop, step)    // generate number array
d3.bin()                       // create histogram bins
d3.group(array, keyFn)         // group into Map
d3.rollup(array, reduceFn, keyFn)  // group + reduce
d3.index(array, keyFn)         // index into Map
d3.sort(array, comparator)
d3.ascending(a, b)
d3.descending(a, b)
d3.bisector(accessor)          // binary search
d3.ticks(start, stop, count)   // nice tick values
d3.tickStep(start, stop, count)
```

---

## d3-scale-chromatic — Color Schemes

### Categorical

```javascript
d3.schemeTableau10             // 10 professional colors
d3.schemeCategory10            // classic D3 10 colors
d3.schemePaired                // 12 paired colors
d3.schemeSet1                  // 9 bold colors
d3.schemeSet2                  // 8 pastel colors
d3.schemeSet3                  // 12 varied colors
d3.schemeDark2                 // 8 dark colors
d3.schemeAccent                // 8 accent colors
```

### Sequential (for continuous data)

```javascript
d3.interpolateBlues
d3.interpolateGreens
d3.interpolateOranges
d3.interpolateReds
d3.interpolatePurples
d3.interpolateGreys
d3.interpolateViridis          // perceptually uniform, colorblind-safe
d3.interpolatePlasma
d3.interpolateInferno
d3.interpolateMagma
d3.interpolateCividis          // colorblind-safe
d3.interpolateWarm
d3.interpolateCool
d3.interpolateTurbo
d3.interpolateYlOrRd           // yellow-orange-red
d3.interpolateYlGnBu           // yellow-green-blue
d3.interpolateBuGn
d3.interpolateBuPu
```

### Diverging (for data with meaningful center)

```javascript
d3.interpolateRdBu             // red-blue
d3.interpolateRdYlGn           // red-yellow-green
d3.interpolateRdYlBu           // red-yellow-blue
d3.interpolatePiYG             // pink-yellow-green
d3.interpolatePRGn             // purple-green
d3.interpolateBrBG             // brown-teal
d3.interpolateSpectral
```

---

## d3-format — Number Formatting

```javascript
d3.format(",.0f")(1234567)    // "1,234,567"
d3.format("$.2f")(42.1)      // "$42.10"
d3.format("+.1%")(0.123)     // "+12.3%"
d3.format(".2s")(42000000)   // "42M"  (SI prefix)
d3.format(",.2~f")(1.10)     // "1.1"  (trim trailing zeros)
```

## d3-time-format — Date Formatting

```javascript
d3.timeFormat("%b %d, %Y")(date)   // "Jan 15, 2024"
d3.timeFormat("%Y-%m-%d")(date)    // "2024-01-15"
d3.timeFormat("%B")(date)          // "January"
d3.timeParse("%Y-%m-%d")("2024-01-15")  // Date object
```

---

## d3-interpolate — Value Interpolation

```javascript
d3.interpolate(a, b)(t)        // auto-detect type
d3.interpolateNumber(a, b)(t)
d3.interpolateString(a, b)(t)  // embedded numbers
d3.interpolateRgb(a, b)(t)
d3.interpolateHsl(a, b)(t)
d3.interpolateHcl(a, b)(t)    // perceptually uniform
d3.interpolateArray(a, b)(t)
d3.interpolateObject(a, b)(t)
d3.piecewise(d3.interpolateRgb, colors)  // multi-stop
```

---

## d3-color — Color Manipulation

```javascript
d3.color("steelblue")          // parse color
d3.rgb(r, g, b, opacity)
d3.hsl(h, s, l, opacity)
d3.lab(l, a, b, opacity)
d3.hcl(h, c, l, opacity)

color.brighter(k)              // lighten
color.darker(k)                // darken
color.copy({opacity: 0.5})     // modify
color.formatHex()              // "#4682b4"
color.formatRgb()              // "rgb(70, 130, 180)"
```

---

## d3-random — Random Number Generation

```javascript
d3.randomUniform(min, max)()
d3.randomNormal(mu, sigma)()
d3.randomLogNormal(mu, sigma)()
d3.randomExponential(lambda)()
d3.randomInt(min, max)()
```
