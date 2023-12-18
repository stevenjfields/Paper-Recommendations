import { useFetchRootPaperQuery } from "../../app/PaperRecommendationsAPI";
import { useAppDispatch, useAppSelector } from "../../app/Hooks";  
import { resetPapers, appendPapers, setSelectedColorScheme, setDepth, toggleLoading } from "../visualization/VisualizationSlice";


export default function LoadingScreen() {
    let root_id = useAppSelector((state)=> state.search.input_value_id);
    let root = useFetchRootPaperQuery(root_id);
    appendPapers([root.data]);
    console.log(useAppSelector((state) => state.visualization.papers));
    toggleLoading();

    return (
        <div className="position-absolute top-50 start-50 translate-middle w-25 h-25">
            <h1>Hello World</h1>
        </div>
    )
}