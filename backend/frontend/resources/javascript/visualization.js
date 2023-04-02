import {Helios} from "https://cdn.skypack.dev/helios-web@=v0.7.0?min";
import { rgb as d3rgb, hsl as d3hsl } from "https://cdn.skypack.dev/d3-color@3";
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";

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

const getSimilarities = async (root, target, sources) => {
    let body = JSON.stringify({
        "root": root,
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
        paper_map.set(i+1, []);

        for (var j = 0; j < current_depth.length; j+=CONCURRENCY_LIMIT) {
            let slice = current_depth.slice(j, j+CONCURRENCY_LIMIT);
            let requests = [];
            slice.forEach((value) => {
                requests.push(fetchReferences(value));
            });

            await Promise.all(requests).then((value) => {
                let next_depth = paper_map.get(i+1);
                paper_map.set(i+1, [next_depth, value].flat(2));
            });
        }
    };
    return paper_map;
};

const getAllPaperSimilarities = async (paper_map, flat_map) => {
    let edges = new Array();
    let root = paper_map.get(0)[0];

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
            let sources = []

            for (var work in works) {
                let object = flat_map.get(works[work]);
                if (object != null) {
                    sources.push(object);
                }
            }

            if (sources.length > 0) {
                reqs.push(getSimilarities(
                    root,
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

let stylizeTooltip = (content,color,x,y,isnew) => {
    if(content){
        tooltipElement.style.left = x + "px";
        tooltipElement.style.top = y + "px";
        if(isnew){
            tooltipElement.style.display = "block";
            let colorRGB = d3rgb(color[0] * 255, color[1] * 255, color[2] * 255);
            let colorHSL = d3hsl(colorRGB);
            if (colorHSL.l>0.35) {
                tooltipElement.style.color = colorRGB.brighter(1.1).formatRgb();
                tooltipElement.style["text-shadow"] = "-1px -1px 1px black, 1px -1px 1px black, -1px 1px 1px black, 1px 1px 1px black";
                // tooltipElement.style["-webkit-text-stroke"] = "1px black";
            } else {
                tooltipElement.style.color = colorRGB.darker(1.1).formatRgb();
                tooltipElement.style["text-shadow"] = "-1px -1px 0px rgba(200,200,200,0.75), 1px -1px 0px rgba(200,200,200,0.75), -1px 1px 0px rgba(200,200,200,0.75), 1px 1px 0px rgba(200,200,200,0.75)";
                // tooltipElement.style["-webkit-text-stroke"] = "1px black";
            }
        }
        tooltipElement.innerText = content;
    }else{
        tooltipElement.style.display = "none";
        tooltipElement.replaceChildren();
    }
}

let showTooltipForNode = (node,edges,x,y,isNew) => {
    if (node) {
        let source_edge = edges.filter((value) => value.source == node.work_id)[0];

        let content = `${node.label}`;

        if (source_edge != null) {
            content += `\nParent Similarity: ${(source_edge.weight * 100).toFixed(1)}`;
            content += `\nRoot Similarity: ${(source_edge.root_weight * 100).toFixed(1)}`;
        }
        stylizeTooltip(content,node.color,x,y,isNew);
    } else {
        stylizeTooltip(null);
    }
}

const log_values = async () => {
    let helios = null;
    let colors = d3.interpolateInferno;

    let paper_map = await getReferencesToDepth();
    let paper_list = new Array();
    let map_iter = paper_map.values();

    let result = map_iter.next();
    while(!result.done) {
        paper_list.push(result.value);
        result = map_iter.next();
    }

    let response = await createEmbeddings(paper_list.flat());

    let flat_map = flat_paper_map(paper_list.flat());

    let edges = await getAllPaperSimilarities(paper_map, flat_map)

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

    helios = new Helios({
        elementID: "visualization", // ID of the element to render the network in
        nodes: node_map, // Dictionary of nodes 
        edges: edges, // Array of edges
        use2D: false, // Choose between 2D or 3D layouts
        fastEdges: false,
    });

    helios.pickeableEdges(Array(edges.length).fill().map((element, index) => index));
    helios.nodesGlobalSizeBase(0.2);
    helios.backgroundColor([0.5,0.5,0.5,1]);
    helios.edgesGlobalOpacityBase(0.9);

    helios.nodeSize((node) => {
        let node_edges = node.edges;
        if (node_edges.length == 0){
            return 0;
        }

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
            let total_root_weight = source_edges.reduce((accumulator, currentValue) => {
                return accumulator + currentValue["root_weight"];
            }, 0)
            let avg_weight = total_weight / source_edges.length;
            let avg_root_weight = total_root_weight / source_edges.length;
            let weight = (avg_weight + avg_root_weight) / 2
    
            let target_nodes = node.neighbors.filter((value) =>
                targets.includes(value.work_id)
            );
            let total_target_size = target_nodes.reduce((accumulator, currentValue) => {
                return accumulator + currentValue.size;
            }, 0);
            let target_size = total_target_size / target_nodes.length;
    
            return weight * target_size;
        }
        return 1;
    });

    helios.nodeColor((node) => {
        let node_color = d3.color(colors(node.size));
        return [node_color["r"]/255,
                node_color["g"]/255,
                node_color["b"]/255,
                node_color["opacity"]];
    });

    helios.onReady(() => {
        helios.zoomFactor(0.05);
        helios.zoomFactor(30,5000);
    });

    helios.onNodeHoverStart((node, event) => {   
        showTooltipForNode(node, edges, event?.clientX, event?.clientY, true);
    });

    helios.onNodeHoverEnd((node, event) => {
        showTooltipForNode(null);
    });

    helios.onNodeClick((node) => {
        setTimeout(() => {
            helios.centerOnNodes([node.ID], 500);
            },
            250
        );
    });

    helios.onNodeDoubleClick((node) => {
        window.open(
            node.url,
            '_blank'
        );
    });

    helios.onEdgeClick((edge) => {
        helios.centerOnNodes(
            [
                edge.source.ID,
                edge.target.ID
            ],
            500
        );
    });
};

document.getElementById("submit").addEventListener("click", log_values);