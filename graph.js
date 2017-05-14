    var filename = 'ircouncil.it.json'
    sigma.parsers.json( filename, {
        container: 'network-graph',
        settings: {
            defaultNodeColor: '#ec5148'
        }},

    function(s) { //This function is passed an instance of Sigma s
        circularGraph(s);
        neighborsBind(s);
        s.startForceAtlas2({worker: true, barnesHutOptimize: false});
    });




// Add a method to the graph model that returns an
// object with every neighbors of a node inside:

sigma.classes.graph.addMethod('neighbors', function(nodeId) {
    var k,
        neighbors = {},
        index = this.allNeighborsIndex[nodeId] || {};

    for (k in index)
      neighbors[k] = this.nodesIndex[k];

    return neighbors;
});


function circularGraph(s){
    s.graph.nodes().forEach(function(node, i, a) {
        node.x = Math.cos(Math.PI * 2 * i / a.length);
        node.y = Math.sin(Math.PI * 2 * i / a.length);
    });
    //Call refresh to render the new graph
    s.refresh();
}


function neighborsBind(s){
    // We first need to save the original colors of our
    // nodes and edges, like this:
    s.graph.nodes().forEach(function(n) {
    n.originalColor = n.color;
    });
    s.graph.edges().forEach(function(e) {
    e.originalColor = e.color;
    });

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
}



