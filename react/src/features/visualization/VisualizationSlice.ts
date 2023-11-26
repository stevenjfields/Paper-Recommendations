import { createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";
import { PaperDetails } from "../../app/PaperRecommendationsAPI";
//import * as d3 from "https://cdn.skypack.dev/d3@7.6.1";

export interface VisualizationState {
    papers: Array<PaperDetails> | null,
    colorSchemes: Array<string>
    selectedColorScheme: string
    depth: number
}

const initialState: VisualizationState = {
    papers: Array<PaperDetails>(),
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
    depth: 3
}

export const VisualizationSlice = createSlice({
    name: "visualization",
    initialState,
    reducers: {
        setSelectedColorScheme: (state: VisualizationState, { payload: value }: PayloadAction<string>) => {
            state.selectedColorScheme = value;
        },
        setDepth: (state: VisualizationState, {payload: value}: PayloadAction<number>) => {
            state.depth = value;
        }
    }
})

export const { setSelectedColorScheme, setDepth } = VisualizationSlice.actions;