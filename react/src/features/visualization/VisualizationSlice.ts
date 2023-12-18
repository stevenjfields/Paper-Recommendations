import { createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";
import { PaperDetails, WeightedEdge, useFetchRootPaperQuery } from "../../app/PaperRecommendationsAPI";
//import * as d3 from "https://cdn.skypack.dev/d3@7.6.1";

export interface VisualizationState {
    papers: Array<PaperDetails> | null
    paperMap: Object
    edges: Array<WeightedEdge>
    colorSchemes: Array<string>
    selectedColorScheme: string
    depth: number,
    loading: Boolean
}

const initialState: VisualizationState = {
    papers: Array<PaperDetails>(),
    paperMap: Object(),
    edges: Array<WeightedEdge>(),
    colorSchemes: [
        "Cividis",
        "Cool",
        "Cubehelix Default",
        "Inferno",
        "Magma",
        "Plasma",
        "Turbo",
        "Viridis",
        "Warm"
    ],
    selectedColorScheme: "Cool",
    depth: 3,
    loading: false
}

export const VisualizationSlice = createSlice({
    name: "visualization",
    initialState,
    reducers: {
        resetPapers: (state: VisualizationState) => {
            state.papers = null;
        },
        appendPapers: (state: VisualizationState, {payload: value}: PayloadAction<Array<PaperDetails>>) => {
            if (state.papers != null)
            {
                state.papers = [...state.papers, ...value]
            } else {
                state.papers = value
            }
        },
        setSelectedColorScheme: (state: VisualizationState, { payload: value }: PayloadAction<string>) => {
            state.selectedColorScheme = value;
        },
        setDepth: (state: VisualizationState, {payload: value}: PayloadAction<number>) => {
            state.depth = value;
        },
        toggleLoading: (state: VisualizationState) => {
            state.loading = !state.loading;
        }
    }
})

export const { resetPapers, appendPapers, setSelectedColorScheme, setDepth, toggleLoading } = VisualizationSlice.actions;