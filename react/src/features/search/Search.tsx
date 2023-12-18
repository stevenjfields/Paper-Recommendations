import { useAutocompleteQuery } from "../../app/OpenAlexAPI";
import { setInputValue, setInputValueId } from "./SearchSlice";
import { useAppSelector, useAppDispatch } from "../../app/Hooks";
import "./Search.css"
import { resetPapers, appendPapers, setSelectedColorScheme, setDepth, toggleLoading } from "../visualization/VisualizationSlice";
import { useFetchRootPaperQuery } from "../../app/PaperRecommendationsAPI";
import React from "react";

export default function Search() {
    const appDispatch = useAppDispatch();
    const selector = useAppSelector;
    const searchState = selector((state) => state.search);
    const visualizationState = selector((state) => state.visualization);
    const {data, error, isLoading} = useAutocompleteQuery(searchState.input_value)

    function handleClick(event: React.MouseEvent<HTMLDivElement>) {
        let title = event.currentTarget.textContent;
        if (title === null) {
            title = "";
        }
        
        let paper = data.results.find((p: { display_name: string | null; }) => p.display_name === title);
        let work_id: string = paper.id.split("/").pop();

        appDispatch(setInputValue(title));
        appDispatch(setInputValueId(work_id));
    }

    function handleSelectChange(event: React.ChangeEvent<HTMLSelectElement>) {
        let value = event.currentTarget.value;
        appDispatch(setSelectedColorScheme(value));
    }

    return (
        <form className="card position-absolute mt-2 ms-2 p-2" autoComplete="off">
            <div className="autocomplete">
                <input type="text" className="search w-100 p-1" placeholder="search for paper..." value={searchState.input_value} onChange={e => appDispatch(setInputValue(e.currentTarget.value))}/>
                <div className="autocomplete-items">
                    {
                        (searchState.show_results && !isLoading) ?
                        data.results.map((item: any) => {
                            return (
                                <div key={item.id} onClick={handleClick}>
                                    {item.display_name}
                                </div>
                            )
                        }) : <></>
                    }
                </div>
            </div>
            <div className="p-1">
                <label htmlFor="depth">Depth (2 to 5):</label>
                <input type="range" min="2" max="5" value={visualizationState.depth} onChange={e => appDispatch(setDepth(Number(e.currentTarget.value)))}></input>
            </div>
            <div className="row p-1">
                <p className="col">Color Scheme: </p>
                <div className="col form">
                    <select className="form-select-sm w-100" aria-label="select" defaultValue={visualizationState.selectedColorScheme} onChange={e => handleSelectChange(e)}>
                        {
                            visualizationState.colorSchemes.map((item) => {
                                return (
                                    <option key={item} value={item}>
                                        {item}
                                    </option>
                                )
                            })
                        }
                    </select>
                </div> 
            </div>
            <input type="button" value="Find similar papers" onClick={e => appDispatch(toggleLoading())}></input>
        </form>
    )
}