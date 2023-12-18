import { Helios } from "helios-web"
import { useEffect, useRef } from 'react'
import Search from "../search/Search";
import { useAppDispatch, useAppSelector } from "../../app/Hooks";
import { useFetchRootPaperQuery } from "../../app/PaperRecommendationsAPI";

export default function Visualization() {
    const heliosReference = useRef(null);
    const root_work_id = useAppSelector((state) => state.search.input_value_id);

    const test = useFetchRootPaperQuery(root_work_id);
    
    console.log(useAppSelector((state) => state.visualization.papers));

    useEffect(() => {

        let nodes = {
        "0": {
            label: "Node 0",
        },
        "1": {
            label: "Node 1",
        },
        "2": {
            label: "Node 2",
        },
        }

        // Edges are arrays of node ids
        let edges = [
        {
            source: "0",
            target: "1",
        },
        {
            source: "1",
            target: "2",
        },
        {
            source: "2",
            target: "0",
        }
        ];

        let helios = new Helios({
        element: heliosReference.current, // ID of the element to render the network in
        nodes: nodes, // Dictionary of nodes 
        edges: edges, // Array of edges
        use2D: false, // Choose between 2D or 3D layouts
        });

        helios.onReady(() => {
        helios.zoomFactor(10);
        helios.zoomFactor(30, 8000);
        });
    }, [])

    return (
        <div>
            <div ref={heliosReference} className="position-absolute" style={{"width": "100%", "height": "100%"}} />
            <Search />
        </div>
    );
}