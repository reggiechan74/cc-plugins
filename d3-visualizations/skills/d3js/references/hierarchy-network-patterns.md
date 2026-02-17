# Hierarchy & Network Patterns — D3.js v7

Patterns for hierarchical data (trees, partitions, packing) and network/graph visualizations (force, Sankey, chord).

---

## Data Preparation

### Hierarchy from Nested JSON

```javascript
// Input: nested object with "children" arrays
const root = d3.hierarchy(nestedData)
  .sum(d => d.value)       // compute values for internal nodes
  .sort((a, b) => b.value - a.value);  // largest first
```

### Hierarchy from Flat Data (Stratify)

```javascript
// Input: flat array with id and parentId
const data = [
  {id: "root", parentId: ""},
  {id: "A", parentId: "root"},
  {id: "B", parentId: "root"},
  {id: "A1", parentId: "A", value: 10},
];

const root = d3.stratify()
  .id(d => d.id)
  .parentId(d => d.parentId)(data)
  .sum(d => d.value);
```

---

## Treemap

Best for showing proportional sizes in a hierarchy.

```javascript
const treemap = d3.treemap()
  .size([width, height])
  .padding(2)
  .round(true);

treemap(root);

const color = d3.scaleOrdinal(d3.schemeTableau10);

svg.selectAll("rect")
  .data(root.leaves())
  .join("rect")
  .attr("x", d => d.x0)
  .attr("y", d => d.y0)
  .attr("width", d => d.x1 - d.x0)
  .attr("height", d => d.y1 - d.y0)
  .attr("fill", d => {
    while (d.depth > 1) d = d.parent;
    return color(d.data.name);
  });

// Labels (only for large enough cells)
svg.selectAll("text")
  .data(root.leaves().filter(d => (d.x1 - d.x0) > 40 && (d.y1 - d.y0) > 14))
  .join("text")
  .attr("x", d => d.x0 + 4)
  .attr("y", d => d.y0 + 14)
  .style("font-size", "11px")
  .text(d => d.data.name);
```

**Tiling algorithms:** `d3.treemapSquarify` (default), `d3.treemapBinary`, `d3.treemapSlice`, `d3.treemapDice`, `d3.treemapSliceDice`.

---

## Sunburst

Best for showing hierarchical relationships with depth.

```javascript
const radius = Math.min(width, height) / 2;

const partition = d3.partition()
  .size([2 * Math.PI, radius]);

partition(root);

const arc = d3.arc()
  .startAngle(d => d.x0)
  .endAngle(d => d.x1)
  .innerRadius(d => d.y0)
  .outerRadius(d => d.y1)
  .padAngle(0.005)
  .padRadius(radius / 2);

const color = d3.scaleOrdinal(d3.quantize(d3.interpolateRainbow, root.children.length + 1));

const g = svg.append("g")
  .attr("transform", `translate(${width / 2},${height / 2})`);

g.selectAll("path")
  .data(root.descendants().filter(d => d.depth))
  .join("path")
  .attr("d", arc)
  .attr("fill", d => {
    while (d.depth > 1) d = d.parent;
    return color(d.data.name);
  })
  .attr("fill-opacity", d => 0.4 + d.depth * 0.2);
```

### Zoomable Sunburst

Add click-to-zoom with animated arc transitions:

```javascript
g.selectAll("path")
  .on("click", (event, p) => {
    root.each(d => {
      d.target = {
        x0: Math.max(0, Math.min(1, (d.x0 - p.x0) / (p.x1 - p.x0))) * 2 * Math.PI,
        x1: Math.max(0, Math.min(1, (d.x1 - p.x0) / (p.x1 - p.x0))) * 2 * Math.PI,
        y0: Math.max(0, d.y0 - p.depth),
        y1: Math.max(0, d.y1 - p.depth)
      };
    });

    const t = g.transition().duration(750);

    g.selectAll("path")
      .transition(t)
      .tween("data", d => {
        const i = d3.interpolate(d.current, d.target);
        return t => d.current = i(t);
      })
      .attrTween("d", d => () => arc(d.current));
  });
```

---

## Circle Packing

Best for showing nested containment and relative sizes.

```javascript
const pack = d3.pack()
  .size([width, height])
  .padding(3);

pack(root);

const color = d3.scaleSequential([0, root.height], d3.interpolateMagma);

svg.selectAll("circle")
  .data(root.descendants())
  .join("circle")
  .attr("cx", d => d.x)
  .attr("cy", d => d.y)
  .attr("r", d => d.r)
  .attr("fill", d => d.children ? color(d.depth) : "white")
  .attr("fill-opacity", d => d.children ? 0.25 : 1)
  .attr("stroke", d => d.children ? color(d.depth) : null);
```

---

## Tree / Dendrogram

Best for showing hierarchical parent-child relationships.

```javascript
const treeLayout = d3.tree()
  .size([height, width - 160]);  // horizontal tree

treeLayout(root);

// Links
svg.selectAll("path.link")
  .data(root.links())
  .join("path")
  .attr("class", "link")
  .attr("fill", "none")
  .attr("stroke", "#ccc")
  .attr("stroke-width", 1.5)
  .attr("d", d3.linkHorizontal()
    .x(d => d.y)
    .y(d => d.x));

// Nodes
const node = svg.selectAll("g.node")
  .data(root.descendants())
  .join("g")
  .attr("class", "node")
  .attr("transform", d => `translate(${d.y},${d.x})`);

node.append("circle")
  .attr("r", 4)
  .attr("fill", d => d.children ? "#555" : "#999");

node.append("text")
  .attr("dy", "0.31em")
  .attr("x", d => d.children ? -8 : 8)
  .attr("text-anchor", d => d.children ? "end" : "start")
  .text(d => d.data.name)
  .style("font-size", "12px");
```

**Variants:**
- **Radial tree**: Use `d3.tree().size([2 * Math.PI, radius])` with polar coordinates
- **Cluster**: Use `d3.cluster()` instead of `d3.tree()` for leaf-aligned layouts

---

## Force-Directed Graph

Best for showing networks and relationships.

```javascript
// Data: { nodes: [{id, group}], links: [{source, target, value}] }

const color = d3.scaleOrdinal(d3.schemeTableau10);

const simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(links).id(d => d.id).distance(50))
  .force("charge", d3.forceManyBody().strength(-200))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("collision", d3.forceCollide().radius(12));

// Links
const link = svg.selectAll("line")
  .data(links)
  .join("line")
  .attr("stroke", "#999")
  .attr("stroke-opacity", 0.6)
  .attr("stroke-width", d => Math.sqrt(d.value));

// Nodes
const node = svg.selectAll("circle")
  .data(nodes)
  .join("circle")
  .attr("r", 8)
  .attr("fill", d => color(d.group))
  .call(drag(simulation));  // see drag pattern below

// Tick
simulation.on("tick", () => {
  link
    .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
  node
    .attr("cx", d => d.x).attr("cy", d => d.y);
});

// Drag behavior
function drag(simulation) {
  return d3.drag()
    .on("start", (event, d) => {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x; d.fy = d.y;
    })
    .on("drag", (event, d) => {
      d.fx = event.x; d.fy = event.y;
    })
    .on("end", (event, d) => {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null; d.fy = null;
    });
}
```

**Tuning tips:**
- `strength(-200)`: Higher magnitude = more repulsion, spread layout
- `distance(50)`: Target link length
- `alphaDecay(0.02)`: Slower = smoother settling
- `forceCollide().radius(r)`: Prevent node overlap

---

## Sankey Diagram

Best for showing flows and quantities between nodes. Requires `d3-sankey` module.

```javascript
import {sankey, sankeyLinkHorizontal} from "https://cdn.jsdelivr.net/npm/d3-sankey@0.12/+esm";

// Data: { nodes: [{name}], links: [{source, target, value}] }
const sankeyLayout = sankey()
  .nodeId(d => d.name)
  .nodeWidth(20)
  .nodePadding(10)
  .extent([[0, 0], [width, height]]);

const {nodes, links} = sankeyLayout({
  nodes: data.nodes.map(d => ({...d})),
  links: data.links.map(d => ({...d}))
});

const color = d3.scaleOrdinal(d3.schemeTableau10);

// Links
svg.selectAll("path.link")
  .data(links)
  .join("path")
  .attr("class", "link")
  .attr("d", sankeyLinkHorizontal())
  .attr("fill", "none")
  .attr("stroke", d => color(d.source.name))
  .attr("stroke-opacity", 0.4)
  .attr("stroke-width", d => Math.max(1, d.width));

// Nodes
svg.selectAll("rect.node")
  .data(nodes)
  .join("rect")
  .attr("class", "node")
  .attr("x", d => d.x0)
  .attr("y", d => d.y0)
  .attr("width", d => d.x1 - d.x0)
  .attr("height", d => d.y1 - d.y0)
  .attr("fill", d => color(d.name));

// Node labels
svg.selectAll("text.node-label")
  .data(nodes)
  .join("text")
  .attr("class", "node-label")
  .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
  .attr("y", d => (d.y0 + d.y1) / 2)
  .attr("dy", "0.35em")
  .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
  .text(d => d.name)
  .style("font-size", "12px");
```

---

## Chord Diagram

Best for showing flows between all pairs in a group.

```javascript
const radius = Math.min(width, height) / 2 - 40;
const innerRadius = radius - 30;

// matrix[i][j] = flow from group i to group j
const chord = d3.chord()
  .padAngle(0.05)
  .sortSubgroups(d3.descending);

const chords = chord(matrix);
const arc = d3.arc().innerRadius(innerRadius).outerRadius(radius);
const ribbon = d3.ribbon().radius(innerRadius);
const color = d3.scaleOrdinal(d3.schemeTableau10);

const g = svg.append("g")
  .attr("transform", `translate(${width / 2},${height / 2})`);

// Arcs (outer ring)
g.selectAll("path.arc")
  .data(chords.groups)
  .join("path")
  .attr("class", "arc")
  .attr("d", arc)
  .attr("fill", d => color(d.index));

// Ribbons (inner connections)
g.selectAll("path.ribbon")
  .data(chords)
  .join("path")
  .attr("class", "ribbon")
  .attr("d", ribbon)
  .attr("fill", d => color(d.source.index))
  .attr("fill-opacity", 0.6);
```

---

## Arc Diagram

Best for showing connections in a compact linear layout.

```javascript
// Nodes arranged along x-axis, links drawn as arcs above/below
const xScale = d3.scalePoint()
  .domain(nodes.map(d => d.id))
  .range([0, width]);

// Links as arcs
svg.selectAll("path.link")
  .data(links)
  .join("path")
  .attr("class", "link")
  .attr("fill", "none")
  .attr("stroke", "#999")
  .attr("stroke-opacity", 0.4)
  .attr("d", d => {
    const x1 = xScale(d.source);
    const x2 = xScale(d.target);
    const r = Math.abs(x2 - x1) / 2;
    return `M${x1},${height / 2} A${r},${r} 0 0,1 ${x2},${height / 2}`;
  });

// Nodes
svg.selectAll("circle")
  .data(nodes)
  .join("circle")
  .attr("cx", d => xScale(d.id))
  .attr("cy", height / 2)
  .attr("r", 5)
  .attr("fill", d => color(d.group));
```

---

## Sample Data Generators

### Hierarchical Data

```javascript
function generateHierarchy(depth = 3, breadth = 4) {
  function makeNode(name, level) {
    if (level >= depth) return {name, value: Math.floor(Math.random() * 100) + 10};
    return {
      name,
      children: d3.range(Math.floor(Math.random() * breadth) + 1)
        .map((_, i) => makeNode(`${name}.${i + 1}`, level + 1))
    };
  }
  return makeNode("root", 0);
}
```

### Network Data

```javascript
function generateNetwork(nodeCount = 30, linkProbability = 0.05) {
  const nodes = d3.range(nodeCount).map(i => ({
    id: `Node ${i}`,
    group: Math.floor(Math.random() * 5)
  }));
  const links = [];
  for (let i = 0; i < nodeCount; i++) {
    for (let j = i + 1; j < nodeCount; j++) {
      if (Math.random() < linkProbability) {
        links.push({source: nodes[i].id, target: nodes[j].id, value: Math.floor(Math.random() * 5) + 1});
      }
    }
  }
  return {nodes, links};
}
```
