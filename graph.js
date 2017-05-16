// Add a method to the graph model that returns an
// object with every neighbors of a node inside:

var a
var colors = [
      '#617db4',
      '#668f3c',
      '#c6583e',
      '#b956af',
      '#FFE77C',
      '#7766B9'
    ];


sigma.classes.graph.addMethod('neighbors', function(nodeId) {
var k,
    neighbors = {},
    index = this.allNeighborsIndex[nodeId] || {};

for (k in index)
  neighbors[k] = this.nodesIndex[k];

return neighbors;
});

sigma.parsers.json('ircouncil.it_sigma.json', {
    container: 'sigma-container',
    renderer: {
        container: document.getElementById('sigma-container'),
        type: 'canvas'
    },
    settings: {
            edgeColor: 'default',
            defaultEdgeColor: '#ccc',
            animationsTime: 5000,
            drawLabels: false,
            scalingMode: 'inside',
            sideMargin: 1,
            minNodeSize: 5,
            maxNodeSize: 30,
            edgeHoverColor: 'edge',
            drawLabels: false,
            borderSize: 1
        }
    },

    function(s) {

        nodes = s.graph.nodes();
        len = nodes.length;

        a = s

        for (i = 0; i < len; i++) {
            nodes[i].x = Math.random();
            nodes[i].y = Math.random();
            nodes[i].size = nodes[i].degree;
            nodes[i].color = colors[nodes[i].modularity];
            nodes[i].label = nodes[i].id;
        }


        // We first need to save the original colors of our
        // nodes and edges, like this:
        s.graph.nodes().forEach(function(n) {
            n.originalColor = n.color;
        });
        s.graph.edges().forEach(function(e) {
            e.originalColor = e.color;
        });

        // Start the layout:
        s.startForceAtlas2({
            worker: true,
//            barnesHutOptimize: true,
//            linLogMode: false,
        	slowDown:1,
//	        adjustSizes: false,
//	        scalingRatio: 1000,
	        gravity: 0.1,
//            barnesHutTheta: 0.5,
            outboundAttractionDistribution: true,
//            autoSettings: false
        });


        //setTimeout(function() {s.stopForceAtlas2();}, 100)
        //setTimeout(function() {s.startNoverlap();}, 5000)


        // When a node is clicked, we check for each node
        // if it is a neighbor of the clicked one. If not,
        // we set its color as grey, and else, it takes its
        // original color.
        // We do the same for the edges, and we only keep
        // edges that have both extremities colored.
        s.bind('clickNode', function(e) {
            var nodeId = e.data.node.id,
                toKeep = s.graph.neighbors(nodeId);
            toKeep[nodeId] = e.data.node;

        s.graph.nodes().forEach(function(n) {
            if (toKeep[n.id])
                n.color = n.originalColor;
            else
                n.color = '#eee';
        });

        s.graph.edges().forEach(function(e) {
            if (toKeep[e.source] && toKeep[e.target])
                e.color = e.originalColor;
            else
                e.color = '#eee';
        });

        // Since the data has been modified, we need to
        // call the refresh method to make the colors
        // update effective.
        s.refresh();
    });

    // When the stage is clicked, we just color each
    // node and edge with its original color.
    s.bind('clickStage', function(e) {
        s.graph.nodes().forEach(function(n) {
            n.color = n.originalColor;
        });

        s.graph.edges().forEach(function(e) {
            e.color = e.originalColor;
        });

        // Same as in the previous event:
        s.refresh();
    });
});