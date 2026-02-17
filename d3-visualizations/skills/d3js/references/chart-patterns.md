# Chart Patterns — D3.js v7

Standard chart type patterns for common data visualizations. Each pattern shows the core D3 code structure, scale choices, and key implementation details.

---

## Bar Chart (Vertical)

Best for comparing categorical values.

```javascript
// Scales
const x = d3.scaleBand()
  .domain(data.map(d => d.category))
  .range([0, width])
  .padding(0.2);

const y = d3.scaleLinear()
  .domain([0, d3.max(data, d => d.value)])
  .nice()
  .range([height, 0]);

// Bars
svg.selectAll("rect")
  .data(data)
  .join("rect")
  .attr("x", d => x(d.category))
  .attr("y", d => y(d.value))
  .attr("width", x.bandwidth())
  .attr("height", d => height - y(d.value))
  .attr("fill", "steelblue");

// Axes
svg.append("g")
  .attr("transform", `translate(0,${height})`)
  .call(d3.axisBottom(x));

svg.append("g")
  .call(d3.axisLeft(y));
```

**Variants:**
- **Horizontal bar**: Swap x/y scales, use `scaleBand` on y-axis
- **Grouped bar**: Use `d3.scaleBand` for groups + inner bands, color by series
- **Stacked bar**: Use `d3.stack()` to compute stacked positions
- **Diverging bar**: Center axis at 0, bars extend left/right (or up/down)

### Stacked Bar

```javascript
const stack = d3.stack()
  .keys(["series1", "series2", "series3"]);

const stacked = stack(data);

const color = d3.scaleOrdinal()
  .domain(["series1", "series2", "series3"])
  .range(d3.schemeTableau10);

svg.selectAll("g.series")
  .data(stacked)
  .join("g")
  .attr("class", "series")
  .attr("fill", d => color(d.key))
  .selectAll("rect")
  .data(d => d)
  .join("rect")
  .attr("x", d => x(d.data.category))
  .attr("y", d => y(d[1]))
  .attr("height", d => y(d[0]) - y(d[1]))
  .attr("width", x.bandwidth());
```

---

## Line Chart

Best for showing trends over time or continuous data.

```javascript
// Scales
const x = d3.scaleTime()
  .domain(d3.extent(data, d => d.date))
  .range([0, width]);

const y = d3.scaleLinear()
  .domain([0, d3.max(data, d => d.value)])
  .nice()
  .range([height, 0]);

// Line generator
const line = d3.line()
  .x(d => x(d.date))
  .y(d => y(d.value))
  .curve(d3.curveMonotoneX); // smooth curve

// Draw line
svg.append("path")
  .datum(data)
  .attr("fill", "none")
  .attr("stroke", "steelblue")
  .attr("stroke-width", 2)
  .attr("d", line);
```

**Variants:**
- **Multi-line**: Group data by series, draw one path per group
- **Area chart**: Use `d3.area()` with `.y0(height)` and `.y1(d => y(d.value))`
- **Missing data**: Use `.defined(d => d.value != null)` on the line generator
- **Stacked area**: Combine `d3.stack()` with `d3.area()`

### Multi-Line Chart

```javascript
const color = d3.scaleOrdinal(d3.schemeTableau10);

const series = d3.group(data, d => d.name);

svg.selectAll("path.line")
  .data(series)
  .join("path")
  .attr("class", "line")
  .attr("fill", "none")
  .attr("stroke", ([name]) => color(name))
  .attr("stroke-width", 2)
  .attr("d", ([, values]) => line(values));
```

### Area Chart

```javascript
const area = d3.area()
  .x(d => x(d.date))
  .y0(height)
  .y1(d => y(d.value))
  .curve(d3.curveMonotoneX);

svg.append("path")
  .datum(data)
  .attr("fill", "steelblue")
  .attr("fill-opacity", 0.3)
  .attr("stroke", "steelblue")
  .attr("stroke-width", 1.5)
  .attr("d", area);
```

---

## Scatter Plot

Best for showing relationships between two quantitative variables.

```javascript
const x = d3.scaleLinear()
  .domain(d3.extent(data, d => d.x)).nice()
  .range([0, width]);

const y = d3.scaleLinear()
  .domain(d3.extent(data, d => d.y)).nice()
  .range([height, 0]);

const color = d3.scaleOrdinal(d3.schemeTableau10);

svg.selectAll("circle")
  .data(data)
  .join("circle")
  .attr("cx", d => x(d.x))
  .attr("cy", d => y(d.y))
  .attr("r", 5)
  .attr("fill", d => color(d.category))
  .attr("opacity", 0.7);
```

**Variants:**
- **Bubble chart**: Map a third variable to radius using `d3.scaleSqrt()`
- **Connected scatterplot**: Add a line connecting points in order
- **Beeswarm**: Use `d3.forceSimulation` to dodge overlapping points

---

## Pie / Donut Chart

Best for showing part-to-whole relationships (few categories).

```javascript
const radius = Math.min(width, height) / 2;
const color = d3.scaleOrdinal(d3.schemeTableau10);

const pie = d3.pie()
  .value(d => d.value)
  .sort(null);

const arc = d3.arc()
  .innerRadius(0)        // 0 for pie, >0 for donut
  .outerRadius(radius);

const labelArc = d3.arc()
  .innerRadius(radius * 0.6)
  .outerRadius(radius * 0.6);

const g = svg.append("g")
  .attr("transform", `translate(${width / 2},${height / 2})`);

g.selectAll("path")
  .data(pie(data))
  .join("path")
  .attr("d", arc)
  .attr("fill", d => color(d.data.label))
  .attr("stroke", "white")
  .attr("stroke-width", 2);

// Labels
g.selectAll("text")
  .data(pie(data))
  .join("text")
  .attr("transform", d => `translate(${labelArc.centroid(d)})`)
  .attr("text-anchor", "middle")
  .text(d => d.data.label);
```

For donut: set `innerRadius` to `radius * 0.5` or similar.

---

## Histogram

Best for showing distribution of a single quantitative variable.

```javascript
const x = d3.scaleLinear()
  .domain(d3.extent(data, d => d.value)).nice()
  .range([0, width]);

const bins = d3.bin()
  .value(d => d.value)
  .domain(x.domain())
  .thresholds(x.ticks(30))(data);

const y = d3.scaleLinear()
  .domain([0, d3.max(bins, d => d.length)]).nice()
  .range([height, 0]);

svg.selectAll("rect")
  .data(bins)
  .join("rect")
  .attr("x", d => x(d.x0) + 1)
  .attr("y", d => y(d.length))
  .attr("width", d => Math.max(0, x(d.x1) - x(d.x0) - 1))
  .attr("height", d => height - y(d.length))
  .attr("fill", "steelblue");
```

---

## Box Plot

Best for comparing distributions across categories.

```javascript
// For each group, compute: min, q1, median, q3, max
function boxStats(values) {
  const sorted = values.sort(d3.ascending);
  const q1 = d3.quantile(sorted, 0.25);
  const median = d3.quantile(sorted, 0.5);
  const q3 = d3.quantile(sorted, 0.75);
  const iqr = q3 - q1;
  const min = Math.max(d3.min(sorted), q1 - 1.5 * iqr);
  const max = Math.min(d3.max(sorted), q3 + 1.5 * iqr);
  return {q1, median, q3, min, max};
}

// Draw box: rect from q1 to q3
// Draw median: line at median
// Draw whiskers: lines from min to q1, q3 to max
// Draw outliers: circles beyond whiskers
```

---

## Heatmap

Best for showing values across two categorical dimensions.

```javascript
const x = d3.scaleBand()
  .domain(xCategories)
  .range([0, width])
  .padding(0.05);

const y = d3.scaleBand()
  .domain(yCategories)
  .range([0, height])
  .padding(0.05);

const color = d3.scaleSequential(d3.interpolateBlues)
  .domain([0, d3.max(data, d => d.value)]);

svg.selectAll("rect")
  .data(data)
  .join("rect")
  .attr("x", d => x(d.xCat))
  .attr("y", d => y(d.yCat))
  .attr("width", x.bandwidth())
  .attr("height", y.bandwidth())
  .attr("fill", d => color(d.value));
```

**Color scale choices:**
- Sequential: `d3.interpolateBlues`, `d3.interpolateViridis`, `d3.interpolateYlOrRd`
- Diverging: `d3.interpolateRdBu`, `d3.interpolatePiYG` (center at 0)

---

## Ridgeline Plot

Best for comparing distributions across many categories with overlap.

```javascript
// One area chart per category, stacked vertically with overlap
const categories = [...new Set(data.map(d => d.category))];
const overlap = 0.8; // fraction of overlap between rows

const yOuter = d3.scalePoint()
  .domain(categories)
  .range([0, height]);

// For each category, compute KDE or histogram, then draw area
categories.forEach(cat => {
  const catData = data.filter(d => d.category === cat);
  const kde = kernelDensityEstimator(kernelEpanechnikov(7), x.ticks(50))(catData.map(d => d.value));

  const yInner = d3.scaleLinear()
    .domain([0, d3.max(kde, d => d[1])])
    .range([0, -yOuter.step() * overlap]);

  const area = d3.area()
    .x(d => x(d[0]))
    .y0(0)
    .y1(d => yInner(d[1]))
    .curve(d3.curveBasis);

  svg.append("path")
    .datum(kde)
    .attr("transform", `translate(0,${yOuter(cat)})`)
    .attr("fill", color(cat))
    .attr("fill-opacity", 0.6)
    .attr("stroke", color(cat))
    .attr("d", area);
});
```

---

## General Tips

### Color Palettes

```javascript
// Categorical (up to 10 categories)
d3.schemeTableau10     // professional, distinct
d3.schemeCategory10    // classic D3
d3.schemePaired        // 12 paired colors

// Sequential (continuous data)
d3.interpolateBlues
d3.interpolateViridis  // colorblind-safe
d3.interpolateYlOrRd   // heat map style

// Diverging (data with meaningful center)
d3.interpolateRdBu     // red-blue
d3.interpolatePRGn     // purple-green
```

### Tooltips

```javascript
const tooltip = d3.select("body").append("div")
  .attr("class", "tooltip")
  .style("position", "absolute")
  .style("background", "white")
  .style("border", "1px solid #ddd")
  .style("border-radius", "4px")
  .style("padding", "8px 12px")
  .style("font-size", "13px")
  .style("pointer-events", "none")
  .style("opacity", 0);

// On elements:
.on("mouseover", (event, d) => {
  tooltip.transition().duration(200).style("opacity", 1);
  tooltip.html(`<strong>${d.label}</strong><br/>Value: ${d.value}`)
    .style("left", (event.pageX + 10) + "px")
    .style("top", (event.pageY - 20) + "px");
})
.on("mouseout", () => {
  tooltip.transition().duration(300).style("opacity", 0);
});
```

### Axes Formatting

```javascript
// Format numbers
svg.append("g").call(d3.axisLeft(y).tickFormat(d3.format(",.0f")));

// Format dates
svg.append("g").call(d3.axisBottom(x).tickFormat(d3.timeFormat("%b %Y")));

// Axis title
svg.append("text")
  .attr("transform", "rotate(-90)")
  .attr("y", -margin.left + 15)
  .attr("x", -height / 2)
  .attr("text-anchor", "middle")
  .style("font-size", "13px")
  .text("Value ($)");
```

### Legends

```javascript
const legend = svg.append("g")
  .attr("transform", `translate(${width - 120}, 0)`);

categories.forEach((cat, i) => {
  const g = legend.append("g")
    .attr("transform", `translate(0, ${i * 22})`);
  g.append("rect")
    .attr("width", 14).attr("height", 14)
    .attr("fill", color(cat));
  g.append("text")
    .attr("x", 20).attr("y", 11)
    .style("font-size", "12px")
    .text(cat);
});
```
