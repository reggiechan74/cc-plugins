# Animation & Interaction Patterns — D3.js v7

Patterns for transitions, zoom, brush, drag, tooltips, and responsive design.

---

## Transitions

Animate changes smoothly between states.

### Basic Transition

```javascript
svg.selectAll("rect")
  .data(newData)
  .join("rect")
  .transition()
  .duration(750)
  .attr("y", d => y(d.value))
  .attr("height", d => height - y(d.value))
  .attr("fill", d => color(d.category));
```

### Enter / Update / Exit with Transitions

```javascript
const bars = svg.selectAll("rect").data(data, d => d.id);

// Exit
bars.exit()
  .transition().duration(300)
  .attr("opacity", 0)
  .attr("height", 0)
  .attr("y", height)
  .remove();

// Update
bars.transition().duration(500)
  .attr("x", d => x(d.category))
  .attr("y", d => y(d.value))
  .attr("width", x.bandwidth())
  .attr("height", d => height - y(d.value));

// Enter
bars.enter()
  .append("rect")
  .attr("x", d => x(d.category))
  .attr("y", height)
  .attr("width", x.bandwidth())
  .attr("height", 0)
  .attr("fill", "steelblue")
  .transition().duration(500)
  .attr("y", d => y(d.value))
  .attr("height", d => height - y(d.value));
```

### Easing Functions

```javascript
.transition()
  .duration(750)
  .ease(d3.easeCubicInOut)   // default-like smooth
  // Other options:
  // d3.easeLinear            - constant speed
  // d3.easeBounce            - bouncing at end
  // d3.easeElastic           - spring-like
  // d3.easeBack              - slight overshoot
  // d3.easeQuadInOut         - gentle acceleration
  // d3.easePoly.exponent(3)  - customizable polynomial
```

### Staggered Transitions

```javascript
svg.selectAll("rect")
  .data(data)
  .join("rect")
  .attr("y", height)
  .attr("height", 0)
  .transition()
  .duration(500)
  .delay((d, i) => i * 50)   // stagger by 50ms per element
  .attr("y", d => y(d.value))
  .attr("height", d => height - y(d.value));
```

### Chained Transitions

```javascript
svg.selectAll("circle")
  .transition().duration(500)
  .attr("r", 20)
  .attr("fill", "orange")
  .transition().duration(500)   // chains after first completes
  .attr("r", 5)
  .attr("fill", "steelblue");
```

---

## Zoom

Enable pan and zoom on visualizations.

### Basic Zoom

```javascript
const zoom = d3.zoom()
  .scaleExtent([0.5, 10])        // min/max zoom
  .translateExtent([[0, 0], [width, height]])  // pan bounds
  .on("zoom", zoomed);

function zoomed(event) {
  contentGroup.attr("transform", event.transform);
}

svg.call(zoom);
```

### Semantic Zoom (rescale axes)

```javascript
const zoom = d3.zoom()
  .scaleExtent([1, 32])
  .on("zoom", (event) => {
    const newX = event.transform.rescaleX(x);
    const newY = event.transform.rescaleY(y);

    xAxisGroup.call(d3.axisBottom(newX));
    yAxisGroup.call(d3.axisLeft(newY));

    svg.selectAll("circle")
      .attr("cx", d => newX(d.x))
      .attr("cy", d => newY(d.y));
  });

svg.call(zoom);
```

### Programmatic Zoom

```javascript
// Zoom to specific area
svg.transition().duration(750).call(
  zoom.transform,
  d3.zoomIdentity
    .translate(width / 2, height / 2)
    .scale(4)
    .translate(-targetX, -targetY)
);

// Reset zoom
svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
```

---

## Brush

Enable rectangular selection.

### One-Dimensional Brush (X-axis)

```javascript
const brush = d3.brushX()
  .extent([[0, 0], [width, height]])
  .on("end", brushed);

function brushed(event) {
  if (!event.selection) return;
  const [x0, x1] = event.selection.map(x.invert);
  // Filter or highlight data in range [x0, x1]
  svg.selectAll("circle")
    .attr("opacity", d => (d.date >= x0 && d.date <= x1) ? 1 : 0.1);
}

svg.append("g").call(brush);
```

### Two-Dimensional Brush

```javascript
const brush = d3.brush()
  .extent([[0, 0], [width, height]])
  .on("end", brushed);

function brushed(event) {
  if (!event.selection) return;
  const [[x0, y0], [x1, y1]] = event.selection;

  svg.selectAll("circle")
    .attr("opacity", d => {
      const cx = x(d.x), cy = y(d.y);
      return (cx >= x0 && cx <= x1 && cy >= y0 && cy <= y1) ? 1 : 0.1;
    });
}

svg.append("g").call(brush);
```

### Brush + Zoom Coordination

```javascript
// Context (small overview) with brush
// Focus (main view) updated by brush selection
const contextBrush = d3.brushX()
  .extent([[0, 0], [width, contextHeight]])
  .on("brush end", ({selection}) => {
    if (!selection) return;
    const [x0, x1] = selection.map(contextX.invert);
    focusX.domain([x0, x1]);
    // Redraw focus area with new domain
    focusLine.attr("d", line);
    focusXAxis.call(d3.axisBottom(focusX));
  });
```

---

## Drag

Enable dragging elements.

### Basic Drag

```javascript
const drag = d3.drag()
  .on("start", (event, d) => {
    d3.select(event.sourceEvent.target).raise().attr("stroke", "black");
  })
  .on("drag", (event, d) => {
    d3.select(event.sourceEvent.target)
      .attr("cx", d.x = event.x)
      .attr("cy", d.y = event.y);
  })
  .on("end", (event, d) => {
    d3.select(event.sourceEvent.target).attr("stroke", null);
  });

svg.selectAll("circle").call(drag);
```

### Drag with Constraints

```javascript
.on("drag", (event, d) => {
  d.x = Math.max(0, Math.min(width, event.x));   // clamp to bounds
  d.y = Math.max(0, Math.min(height, event.y));
  d3.select(event.sourceEvent.target)
    .attr("cx", d.x)
    .attr("cy", d.y);
})
```

---

## Tooltips

### HTML Tooltip (most flexible)

```javascript
const tooltip = d3.select("body").append("div")
  .style("position", "absolute")
  .style("background", "white")
  .style("border", "1px solid #ddd")
  .style("border-radius", "4px")
  .style("padding", "8px 12px")
  .style("font-size", "13px")
  .style("box-shadow", "0 2px 4px rgba(0,0,0,0.1)")
  .style("pointer-events", "none")
  .style("opacity", 0)
  .style("transition", "opacity 0.2s");

elements
  .on("mouseover", (event, d) => {
    tooltip.style("opacity", 1)
      .html(`
        <strong>${d.name}</strong><br/>
        Value: ${d3.format(",.0f")(d.value)}<br/>
        <span style="color:#666">${d.category}</span>
      `);
  })
  .on("mousemove", (event) => {
    tooltip
      .style("left", (event.pageX + 12) + "px")
      .style("top", (event.pageY - 28) + "px");
  })
  .on("mouseout", () => {
    tooltip.style("opacity", 0);
  });
```

### SVG Title Tooltip (simple)

```javascript
elements.append("title")
  .text(d => `${d.name}: ${d.value}`);
```

### Crosshair / Bisect Tooltip (for line charts)

```javascript
const bisect = d3.bisector(d => d.date).center;

const focus = svg.append("g").style("display", "none");
focus.append("line").attr("class", "crosshair-y")
  .attr("stroke", "#999").attr("stroke-dasharray", "3,3");
focus.append("circle").attr("r", 4).attr("fill", "steelblue");
focus.append("text").attr("dy", -10).attr("text-anchor", "middle");

svg.append("rect")
  .attr("width", width).attr("height", height)
  .attr("fill", "none").attr("pointer-events", "all")
  .on("mouseover", () => focus.style("display", null))
  .on("mouseout", () => focus.style("display", "none"))
  .on("mousemove", (event) => {
    const x0 = x.invert(d3.pointer(event)[0]);
    const i = bisect(data, x0);
    const d = data[i];
    focus.attr("transform", `translate(${x(d.date)},${y(d.value)})`);
    focus.select("text").text(d3.format(",.0f")(d.value));
    focus.select(".crosshair-y")
      .attr("y1", 0).attr("y2", height - y(d.value));
  });
```

---

## Responsive Design

### ViewBox Approach (recommended)

```javascript
const svg = d3.select("#chart")
  .append("svg")
  .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
  .attr("preserveAspectRatio", "xMidYMid meet")
  .style("max-width", "100%")
  .style("height", "auto");
```

### Resize Observer

```javascript
const resizeObserver = new ResizeObserver(entries => {
  for (const entry of entries) {
    const {width: containerWidth} = entry.contentRect;
    const newWidth = containerWidth - margin.left - margin.right;
    // Update scales, axes, and elements
    x.range([0, newWidth]);
    xAxisGroup.call(d3.axisBottom(x));
    // Redraw elements...
  }
});

resizeObserver.observe(document.getElementById("chart"));
```

### Debounced Window Resize

```javascript
let resizeTimer;
window.addEventListener("resize", () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    const newWidth = container.clientWidth - margin.left - margin.right;
    // Rebuild chart with new dimensions
  }, 250);
});
```

---

## Animation Patterns

### Loading Animation (bars growing from bottom)

```javascript
svg.selectAll("rect")
  .data(data)
  .join("rect")
  .attr("x", d => x(d.category))
  .attr("width", x.bandwidth())
  .attr("y", height)           // start at bottom
  .attr("height", 0)           // start with no height
  .attr("fill", "steelblue")
  .transition()
  .duration(800)
  .delay((d, i) => i * 80)    // stagger
  .ease(d3.easeCubicOut)
  .attr("y", d => y(d.value))
  .attr("height", d => height - y(d.value));
```

### Data Update Animation

```javascript
function update(newData) {
  // Update scales
  y.domain([0, d3.max(newData, d => d.value)]).nice();
  yAxisGroup.transition().duration(500).call(d3.axisLeft(y));

  // Update bars
  svg.selectAll("rect")
    .data(newData, d => d.category)
    .join(
      enter => enter.append("rect")
        .attr("x", d => x(d.category))
        .attr("width", x.bandwidth())
        .attr("y", height)
        .attr("height", 0)
        .attr("fill", "steelblue")
        .call(enter => enter.transition().duration(500)
          .attr("y", d => y(d.value))
          .attr("height", d => height - y(d.value))),
      update => update
        .call(update => update.transition().duration(500)
          .attr("y", d => y(d.value))
          .attr("height", d => height - y(d.value))),
      exit => exit
        .call(exit => exit.transition().duration(300)
          .attr("opacity", 0).remove())
    );
}
```

### Morphing Between Chart Types

```javascript
// From bar to scatter: transition rect → circle positions
svg.selectAll("rect")
  .transition().duration(750)
  .attr("width", 8)
  .attr("height", 8)
  .attr("rx", 4)  // round corners to look like circles
  .attr("x", d => xScatter(d.x) - 4)
  .attr("y", d => yScatter(d.y) - 4);
```

---

## Keyboard Accessibility

```javascript
// Make elements focusable and keyboard-navigable
svg.selectAll("rect")
  .attr("tabindex", 0)
  .attr("role", "img")
  .attr("aria-label", d => `${d.category}: ${d.value}`)
  .on("keydown", (event, d) => {
    if (event.key === "Enter" || event.key === " ") {
      // Trigger same action as click
      handleClick(event, d);
    }
  });
```
