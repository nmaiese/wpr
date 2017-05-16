var node
var link


var padding = 1, // separation between circles
    radius=8;

function collide(alpha) {
  var quadtree = d3.geom.quadtree(graph.nodes);
  return function(d) {
    var rb = 2*radius + padding,
        nx1 = d.x - rb,
        nx2 = d.x + rb,
        ny1 = d.y - rb,
        ny2 = d.y + rb;
    quadtree.visit(function(quad, x1, y1, x2, y2) {
      if (quad.point && (quad.point !== d)) {
        var x = d.x - quad.point.x,
            y = d.y - quad.point.y,
            l = Math.sqrt(x * x + y * y);
          if (l < rb) {
          l = (l - rb) / l * alpha;
          d.x -= x *= l;
          d.y -= y *= l;
          quad.point.x += x;
          quad.point.y += y;
        }
      }
      return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;
    });
  };
}


function normalizeSize(data, min=5, max=20){
    dmax = d3.max(data, function(d){ return d.degree });
    dmin = d3.min(data, function(d){ return d.degree });
    data.forEach(function(d){
        d['size'] = min + (((d.degree - dmin)*(max-min)) / (dmax - dmin))
    })

    return data
}



//Constants for the SVG
var width = Math.max(document.documentElement.clientWidth, window.innerWidth || 0)-100;
var height = Math.max(document.documentElement.clientHeight, window.innerHeight || 0)-100;

//Set up the colour scale
var color = d3.scale.category10();

//Set up the force layout
var force = d3.layout.force()
    .gravity(0.05)
    .linkDistance(30)
    .charge(-120)
    .size([width, height]);

//Append a SVG to the body of the html page. Assign this SVG as an object to svg
var svg = d3.select("#d3-container").append("svg")
    .attr("width", width)
    .attr("height", height);

//Read the data from the mis element

var graph
var datum

d3.json("ircouncil.it_d3.json", function(error, data) {
    data.nodes = normalizeSize(data.nodes, min=5, max=20);
    graph = data;
    graphRec=JSON.parse(JSON.stringify(graph)); //Add this line


    //Creates the graph data structure out of the json data
    force.nodes(graph.nodes)
        .links(graph.links)
        .start();

    //Create all the line svgs but without locations yet
    link = svg.selectAll(".link")
        .data(graph.links)
        .enter().append("line")
        .attr("class", "link");

    //Do the same with the circles for the nodes - no
    node = svg.selectAll(".node")
        .data(graph.nodes)
        .enter().append("circle")
        .attr("class", "node")
        .attr("r", function(d){  return d.size })

        .style("fill", function (d) {
        return color(d.modularity);
    }).call(force.drag);


    //Now we are giving the SVGs co-ordinates - the force layout is generating the co-ordinates which this code is using to update the attributes of the SVG elements
    force.on("tick", function () {
        link.attr("x1", function (d) {
            return d.source.x;
        })
            .attr("y1", function (d) {
            return d.source.y;
        })
            .attr("x2", function (d) {
            return d.target.x;
        })
            .attr("y2", function (d) {
            return d.target.y;
        });
        node.attr("cx", function (d) {
            return d.x;
        })
            .attr("cy", function (d) {
            return d.y;
        });
         node.each(collide(0.6)); //Added
    });




})

