/**
 * D3.js + React Example — Scatter Plot Component
 *
 * Usage:
 *   import { ScatterPlot } from "./ScatterPlot";
 *   <ScatterPlot data={data} width={700} height={450} />
 *
 * Install D3: npm install d3 @types/d3
 */

import { useRef, useEffect } from "react";
import * as d3 from "d3";

interface DataPoint {
  x: number;
  y: number;
  category: string;
  label: string;
}

interface ScatterPlotProps {
  data?: DataPoint[];
  width?: number;
  height?: number;
}

// Sample data (used when no data prop is provided)
const sampleData: DataPoint[] = [
  { x: 12, y: 45, category: "A", label: "Alpha-1" },
  { x: 28, y: 78, category: "A", label: "Alpha-2" },
  { x: 35, y: 52, category: "A", label: "Alpha-3" },
  { x: 42, y: 89, category: "B", label: "Beta-1" },
  { x: 55, y: 63, category: "B", label: "Beta-2" },
  { x: 61, y: 95, category: "B", label: "Beta-3" },
  { x: 18, y: 30, category: "C", label: "Gamma-1" },
  { x: 72, y: 41, category: "C", label: "Gamma-2" },
  { x: 85, y: 72, category: "C", label: "Gamma-3" },
  { x: 90, y: 55, category: "A", label: "Alpha-4" },
  { x: 48, y: 82, category: "B", label: "Beta-4" },
  { x: 33, y: 67, category: "C", label: "Gamma-4" },
];

export function ScatterPlot({ data = sampleData, width = 700, height = 450 }: ScatterPlotProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const margin = { top: 30, right: 30, bottom: 50, left: 60 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Clear previous render
    d3.select(svgRef.current).selectAll("*").remove();

    const svg = d3.select(svgRef.current)
      .attr("viewBox", `0 0 ${width} ${height}`)
      .attr("preserveAspectRatio", "xMidYMid meet")
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Scales
    const x = d3.scaleLinear()
      .domain(d3.extent(data, d => d.x) as [number, number]).nice()
      .range([0, innerWidth]);

    const y = d3.scaleLinear()
      .domain(d3.extent(data, d => d.y) as [number, number]).nice()
      .range([innerHeight, 0]);

    const color = d3.scaleOrdinal<string>()
      .domain([...new Set(data.map(d => d.category))])
      .range(["#4f6d8e", "#d97757", "#6b9e78"]);

    // Axes
    svg.append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(d3.axisBottom(x))
      .selectAll("text")
      .style("font-size", "11px");

    svg.append("g")
      .call(d3.axisLeft(y))
      .selectAll("text")
      .style("font-size", "11px");

    // Axis labels
    svg.append("text")
      .attr("x", innerWidth / 2)
      .attr("y", innerHeight + 40)
      .attr("text-anchor", "middle")
      .style("font-size", "13px")
      .style("fill", "#6b7280")
      .text("X Value");

    svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", -margin.left + 18)
      .attr("x", -innerHeight / 2)
      .attr("text-anchor", "middle")
      .style("font-size", "13px")
      .style("fill", "#6b7280")
      .text("Y Value");

    // Tooltip
    const tooltip = d3.select(tooltipRef.current);

    // Dots
    svg.selectAll("circle")
      .data(data)
      .join("circle")
      .attr("cx", d => x(d.x))
      .attr("cy", d => y(d.y))
      .attr("r", 0)
      .attr("fill", d => color(d.category))
      .attr("opacity", 0.8)
      .attr("stroke", "white")
      .attr("stroke-width", 1.5)
      .on("mouseover", (event: MouseEvent, d: DataPoint) => {
        tooltip.style("opacity", "1")
          .html(`<strong>${d.label}</strong><br/>x: ${d.x}, y: ${d.y}<br/>Category: ${d.category}`);
      })
      .on("mousemove", (event: MouseEvent) => {
        tooltip
          .style("left", (event.pageX + 12) + "px")
          .style("top", (event.pageY - 30) + "px");
      })
      .on("mouseout", () => {
        tooltip.style("opacity", "0");
      })
      .transition()
      .duration(500)
      .delay((_, i) => i * 40)
      .attr("r", 7);

    // Legend
    const categories = [...new Set(data.map(d => d.category))];
    const legend = svg.append("g")
      .attr("transform", `translate(${innerWidth - 80}, 0)`);

    categories.forEach((cat, i) => {
      const g = legend.append("g").attr("transform", `translate(0, ${i * 22})`);
      g.append("circle").attr("r", 5).attr("cx", 5).attr("cy", 5).attr("fill", color(cat));
      g.append("text").attr("x", 16).attr("y", 9).style("font-size", "12px").text(cat);
    });

  }, [data, width, height]);

  return (
    <div style={{ position: "relative" }}>
      <svg ref={svgRef} style={{ maxWidth: "100%", height: "auto" }} />
      <div
        ref={tooltipRef}
        style={{
          position: "absolute",
          background: "white",
          border: "1px solid #e5e7eb",
          borderRadius: "6px",
          padding: "8px 12px",
          fontSize: "13px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
          pointerEvents: "none",
          opacity: 0,
          transition: "opacity 0.2s",
        }}
      />
    </div>
  );
}
