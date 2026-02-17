import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";

// --- Sample Data ---
const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

const data = [
  { city: "San Francisco", values: [11, 12, 13, 14, 15, 16, 17, 18, 18, 16, 13, 11] },
  { city: "New York", values: [1, 2, 7, 13, 18, 23, 26, 25, 21, 15, 9, 3] },
];

const series = data.flatMap(d =>
  d.values.map((temp, i) => ({ city: d.city, month: months[i], monthIndex: i, temp }))
);

// --- Dimensions ---
const margin = { top: 30, right: 120, bottom: 50, left: 60 };
const width = 700 - margin.left - margin.right;
const height = 400 - margin.top - margin.bottom;

// --- SVG ---
const svg = d3.select("#chart")
  .append("svg")
  .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
  .attr("preserveAspectRatio", "xMidYMid meet")
  .style("max-width", "100%")
  .style("height", "auto")
  .append("g")
  .attr("transform", `translate(${margin.left},${margin.top})`);

// --- Scales ---
const x = d3.scalePoint()
  .domain(months)
  .range([0, width])
  .padding(0.5);

const y = d3.scaleLinear()
  .domain([d3.min(series, d => d.temp) - 2, d3.max(series, d => d.temp) + 2])
  .nice()
  .range([height, 0]);

const color = d3.scaleOrdinal()
  .domain(data.map(d => d.city))
  .range(["#4f6d8e", "#d97757"]);

// --- Axes ---
svg.append("g")
  .attr("transform", `translate(0,${height})`)
  .call(d3.axisBottom(x))
  .selectAll("text")
  .style("font-size", "12px");

svg.append("g")
  .call(d3.axisLeft(y).tickFormat(d => `${d}°C`))
  .selectAll("text")
  .style("font-size", "11px");

// Y-axis label
svg.append("text")
  .attr("transform", "rotate(-90)")
  .attr("y", -margin.left + 18)
  .attr("x", -height / 2)
  .attr("text-anchor", "middle")
  .style("font-size", "13px")
  .style("fill", "#6b7280")
  .text("Temperature (°C)");

// --- Line generator ---
const line = d3.line()
  .x(d => x(d.month))
  .y(d => y(d.temp))
  .curve(d3.curveMonotoneX);

// --- Tooltip ---
const tooltip = d3.select("#tooltip");

// --- Draw lines ---
const grouped = d3.group(series, d => d.city);

for (const [city, values] of grouped) {
  // Line
  svg.append("path")
    .datum(values)
    .attr("class", "line")
    .attr("stroke", color(city))
    .attr("d", line);

  // Dots
  svg.selectAll(`.dot-${city.replace(/\s/g, "")}`)
    .data(values)
    .join("circle")
    .attr("class", "dot")
    .attr("cx", d => x(d.month))
    .attr("cy", d => y(d.temp))
    .attr("r", 4)
    .attr("fill", color(city))
    .attr("stroke", "white")
    .attr("stroke-width", 1.5)
    .on("mouseover", (event, d) => {
      tooltip.style("opacity", 1)
        .html(`<strong>${d.city}</strong><br/>${d.month}: ${d.temp}°C`);
    })
    .on("mousemove", (event) => {
      tooltip.style("left", (event.pageX + 12) + "px").style("top", (event.pageY - 30) + "px");
    })
    .on("mouseout", () => tooltip.style("opacity", 0));
}

// --- Legend ---
const legend = svg.append("g")
  .attr("transform", `translate(${width + 15}, 0)`);

data.forEach((d, i) => {
  const g = legend.append("g").attr("transform", `translate(0, ${i * 24})`);
  g.append("line").attr("x1", 0).attr("x2", 20).attr("y1", 7).attr("y2", 7)
    .attr("stroke", color(d.city)).attr("stroke-width", 2);
  g.append("circle").attr("cx", 10).attr("cy", 7).attr("r", 4)
    .attr("fill", color(d.city)).attr("stroke", "white").attr("stroke-width", 1.5);
  g.append("text").attr("x", 28).attr("y", 11).style("font-size", "12px").text(d.city);
});
