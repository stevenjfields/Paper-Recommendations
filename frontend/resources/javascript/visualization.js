import {Helios} from "https://cdn.skypack.dev/helios-web?min";

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

const getAllPaperSimilarities = async (paper_map) => {
    let edges = new Array();

    for (var i = 0; i < paper_map.size-1; i++) {
        let current_depth = paper_map.get(i);
        let next_depth = paper_map.get(i+1);

        //huge bottle neck atm
        for (var paper of current_depth) {
            let sims = await getSimilarities(
                paper,
                next_depth.filter(element => {
                    if (paper.references.length > 0) {
                        return paper.references.includes(element.work_id);
                    } else {
                        return paper.related.includes(element.work_id);
                    }
                })
            );
            edges.push(sims);
        }
    }

    return edges.flat();
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

    let edges = await getAllPaperSimilarities(paper_map)
    console.log(edges);

    let node_map = {};
    paper_list.flat().forEach(paper => {
        let entry_id = paper.work_id;
        let entry = {
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
    });
  
    helios.onReady(() => {
        helios.zoomFactor(0.05);
        helios.zoomFactor(30,8000);
    });

    helios.edgeWidth((sourceNode, targetNode, edgeIndex) => {
        let weight = edges[edgeIndex.weight];
        return [weight, weight];
      });

    helios.onNodeHoverStart((node) => {
        console.log(`Node hovered: ${node.label}, ${node.url}`);
    });

    helios.onEdgeClick((edge) => {
        console.log(edge);
    });
};

document.getElementById("submit").addEventListener("click", log_values);