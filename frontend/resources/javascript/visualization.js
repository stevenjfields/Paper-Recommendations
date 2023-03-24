import {Helios} from "https://cdn.skypack.dev/helios-web@~v0.7.0?min";

const fetchRootPaperDetails = async () => {
    let response = await fetch(
        `http://0.0.0.0:8080/paper/${selected_paper_id}`,
        {
            mode: "cors",
            method: "GET",
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            }
        }
    ).then(res => res.json());

    return response
};

const fetchReferences = async (paper) => {
    let response = await fetch(
        `http://0.0.0.0:8080/references/`,
        {
            mode: "cors",
            method: "POST",
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            },
            body: JSON.stringify(paper)
        }
    ).then(res => res.json());

    return response
};

const createEmbeddings = async (paper_list) => {
    let response = await fetch(
        `http://0.0.0.0:8080/embeddings/`,
        {
            mode: "cors",
            method: "POST",
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            },
            body: JSON.stringify(paper_list)
        }
    ).then(res => res.json());

    return response
};

const getSimilarities = async (target, sources) => {
    let body = JSON.stringify({
        "target": target,
        "sources": sources
    });

    let response = await fetch(
        `http://0.0.0.0:8080/similarities/`,
        {
            mode: "cors",
            method: "POST",
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            },
            body: body
        }
    ).then(res => res.json());

    return response
};

const getReferencesToDepth = async () => {
    let paper_map = new Map();

    let result = [await fetchRootPaperDetails()];
    paper_map.set(0, result);

    for (var i = 0; i < depth_input.value-1; i++) {
        let current_depth = paper_map.get(i);

        for (var paper of current_depth) {
            if (paper_map.has(i+1)) {
                let next = paper_map.get(i+1);
                let refs = await fetchReferences(paper);
                paper_map.set(i+1, [next, refs].flat());
            } else {
                paper_map.set(i+1, await fetchReferences(paper));
            }
        }
    };
    return paper_map;
};

const getAllPaperSimilarities = async (paper_map, flat_map) => {
    let edges = new Array();

    for (var i = 0; i < paper_map.size-1; i++) {
        let current_depth = paper_map.get(i);
        let next_depth = paper_map.get(i+1);

        let reqs = [];

        for (var paper of current_depth) {

            let works = []
            if (paper.references.length > 0) {
                works = paper.references;
            } else {
                works = paper.related;
            }
            let sources = [];

            for (var work in works) {
                let object = flat_map.get(works[work]);
                if (object != null) {
                    sources.push(object);
                }
            }

            if (sources.length > 0) {
                reqs.push(await getSimilarities(
                    paper,
                    sources
                ));
            }
        }

        await Promise.all(reqs).then(
            results => edges.push(results)
        );
    }

    return edges.flat(Infinity)
};

const flat_paper_map = (paper_list) => {
    let flat_map = new Map();
    
    for (var paper in paper_list) {
        flat_map.set(paper_list[paper].work_id, paper_list[paper]);
    }

    return flat_map;
};

const log_values = async () => {
    let paper_map = await getReferencesToDepth();
    console.log(paper_map)
    let paper_list = new Array();
    let map_iter = paper_map.values();

    let result = map_iter.next();
    while(!result.done) {
        console.log(result.value);
        paper_list.push(result.value);
        result = map_iter.next();
    }

    let response = await createEmbeddings(paper_list.flat());
    console.log(response)

    let flat_map = flat_paper_map(paper_list.flat());

    let edges = await getAllPaperSimilarities(paper_map, flat_map)
    console.log(edges);

    let node_map = {};
    paper_list.flat().forEach(paper => {
        let entry_id = paper.work_id;
        let entry = {
            "work_id": paper.work_id,
            "label":  paper.title,
            "url": paper.landing_page_url
        };
        node_map[entry_id] = entry;
    });
    console.log(node_map);

    let helios = new Helios({
        elementID: "visualization", // ID of the element to render the network in
        nodes: node_map, // Dictionary of nodes 
        edges: edges, // Array of edges
        use2D: false, // Choose between 2D or 3D layouts
        fastEdges: false,
    });

    helios.pickeableEdges(Array(edges.length).fill().map((element, index) => index));
    helios.nodesGlobalSizeBase(0.1);

    helios.nodeSize((node) => {
        let node_edges = node.edges;
        let filtered = edges.filter((value, index) => node_edges.includes(index));
        let targets = [];

        let source_edges = filtered.filter((value) => {
            targets.push(value.target);
            return value.source == node.work_id;
        });

        if (source_edges.length > 0) {
            let total_weight = source_edges.reduce((accumulator, currentValue) => {
                return accumulator + currentValue["weight"];
            }, 0);
            let avg_weight = total_weight / source_edges.length;
    
            let target_nodes = node.neighbors.filter((value) =>
                targets.includes(value.work_id)
            );
            let total_target_size = target_nodes.reduce((accumulator, currentValue) => {
                return accumulator + currentValue.size;
            }, 0);
            let target_size = total_target_size / target_nodes.length;
    
            return avg_weight * target_size;
        }
        return 1;
    });

    helios.onReady(() => {
        helios.zoomFactor(0.05);
        helios.zoomFactor(30,8000);
    });

    helios.onNodeHoverStart((node) => {
        console.log(`Node hovered: ${node.label}, ${node.url}`);
        console.log(node.edges)
        let node_edges = node.edges;
        let filtered = edges.filter((value, index) => node_edges.includes(index));
        let targets = [];

        let source_edges = filtered.filter((value) => {
            targets.push(value.target);
            return value.source == node.work_id;
        });
        let total_weight = source_edges.reduce((accumulator, currentValue) => {
            return accumulator + currentValue["weight"];
        }, 0);
        let avg_weight = total_weight / source_edges.length;

        let target_nodes = node.neighbors.filter((value) =>
            targets.includes(value.work_id)
        );
        let total_target_size = target_nodes.reduce((accumulator, currentValue) => {
            return accumulator + currentValue.size;
        }, 0);
        let target_size = total_target_size / target_nodes.length;

        return avg_weight * target_size;
    });

    helios.onNodeClick((node) => {
        window.open(
            node.url,
            '_blank'
        );
    });

    helios.onEdgeHoverStart((edge) => {
        console.log(edge);
        console.log(edges[edge.index]);
    });
};

document.getElementById("submit").addEventListener("click", log_values);