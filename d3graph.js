var width,height
var chartWidth, chartHeight
var margin
var svg = d3.select("#d3-container").append("svg")
var chartLayer = svg.append("g").classed("chartLayer", true)
var colors = d3.schemeCategory10
var a, b

// Define the div for the tooltip
var div = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);




function normalizeSize(data, min=5, max=20){
    dmax = d3.max(data, function(d){ return d.degree });
    dmin = d3.min(data, function(d){ return d.degree });
    data.forEach(function(d){
        d['size'] = min + (((d.degree - dmin)*(max-min)) / (dmax - dmin))
    })

    return data
}


function setSize(data) {
    var width = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    var height = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);

    margin = {top:0, left:0, bottom:0, right:0 }


    chartWidth = width - (margin.left+margin.right)
    chartHeight = height - (margin.top+margin.bottom)

    svg.attr("width", width).attr("height", height)


    chartLayer
        .attr("width", chartWidth)
        .attr("height", chartHeight)
        .attr("transform", "translate("+[margin.left, margin.top]+")")

}



function drawChart(data) {
    var simulation = d3.forceSimulation()
        .force("link", d3.forceLink().id(function(d) { return d.index }))
        .force("collide",d3.forceCollide( function(d){ return d.size }).iterations(1) )
        .force("charge", d3.forceManyBody().strength(-400))
        .force("center", d3.forceCenter(chartWidth / 2, chartHeight / 2))
        .force("y", d3.forceY(0))
        .force("x", d3.forceX(0))

    var link = svg.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(data.links)
        .enter()
        .append("line")
        .attr("stroke", "black")


    var node = svg.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(data.nodes)
        .enter().append("circle")
        .attr("r", function(d){  return d.size })
        .style("fill", function(d){ return colors[d.modularity] })
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended))
        .on("mouseover", function(d) {
            div.transition()
                .duration(200)
                .style("opacity", .9);
            div.html(d.id)
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px")
                .style("width" ,d.id.length + 200);
        })
        .on("mouseout", function(d) {
            div.style("opacity", 0);
        })
        .on('click', connectedNodes);
    // The label each node its node number from the networkx graph.
    node.append("title")
        .text(function(d) { return "Node: " + d.id + "\n" + "Degree: " + d.degree + "\n" });



    var ticked = function() {
        link
            .attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });

        node
            .attr("cx", function(d) { return d.x; })
            .attr("cy", function(d) { return d.y; });
    }

    //Toggle stores whether the highlighting is on
    var toggle = 0;


    function connectedNodes() {
        if (toggle == 0) {
            //Reduce the opacity of all but the neighbouring nodes to 0.3.
            var d = d3.select(this).node().__data__;
            //Reduce the opacity of all but the neighbouring edges to 0.8.
            link.style("opacity", function (o) {
                return d.index==o.source.index | d.index==o.target.index ? 1 : 0.3;
            });
            //Increases the stroke width of the neighbouring edges.
            link.style("stroke-width", function (o) {
                return d.index==o.source.index | d.index==o.target.index ? 1.5 : 0.3;
            });
            //Reset the toggle.
            toggle = 1;

        } else {
            //Restore everything back to normal
            node.style("opacity", 1);
            link.style("opacity", 1);
            link.style("stroke-width", 0.6);
            toggle = 0;
        }
    }

    simulation
        .nodes(data.nodes)
        .on("tick", ticked);

    simulation.force("link")
        .links(data.links);



    function dragstarted(d) {
        if (!d3.event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
    }

    function dragended(d) {
        if (!d3.event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

}


//
//d3.json("ircouncil.it.json", function(error, graph) {
//    // Within this block, the network has been loaded
//    // and stored in the 'graph' object.
//
//    // We load the nodes and links into the force-directed
//    // graph and initialise the dynamics.
//    force.nodes(graph.nodes)
//        .links(graph.links)
//        .start();
//
//    // We create a < line> SVG element for each link
//    // in the graph.
//    var link = svg.selectAll(".link")
//        .data(graph.links)
//        .enter().append("line")
//        .attr("class", "link");
//
//    // We create a < circle> SVG element for each node
//    // in the graph, and we specify a few attributes.
//    var node = svg.selectAll(".node")
//        .data(graph.nodes)
//        .enter().append("circle")
//        .attr("class", "node")
//        .attr("r", 5)  // radius
//        .style("fill", function(d) {
//            // We colour the node depending on the degree.
//            return color(d.degree);
//        })
//        .call(force.drag);
//
//    // The label each node its node number from the networkx graph.
//    node.append("title")
//        .text(function(d) { return d.id; });
//
//
//
//    // We bind the positions of the SVG elements
//    // to the positions of the dynamic force-directed graph,
//    // at each time step.
//    force.on("tick", function() {
//        link.attr("x1", function(d) { return d.source.x; })
//            .attr("y1", function(d) { return d.source.y; })
//            .attr("x2", function(d) { return d.target.x; })
//            .attr("y2", function(d) { return d.target.y; });
//
//        node.attr("cx", function(d) { return d.x; })
//            .attr("cy", function(d) { return d.y; });
//    });
//});
