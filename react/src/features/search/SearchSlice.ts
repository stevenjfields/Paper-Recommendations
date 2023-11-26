import { createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";

export interface SearchState {
    input_value: string,
    input_value_id: string
    autocomplete_results: Array<string> | null
    show_results: boolean
}

const initialState: SearchState = {
    input_value: "Attention is all you need",
    input_value_id: "W2963403868",
    autocomplete_results: null,
    show_results: false
}

export const SearchSlice = createSlice({
    name: "search",
    initialState,
    reducers: {
        setInputValue: (state: SearchState, { payload : value }: PayloadAction<string>) => {
            state.input_value = value;
            state.show_results = true;
        },
        setInputValueId: (state: SearchState, action: PayloadAction<string>) => {
            state.input_value_id = action.payload;
            state.show_results = false;
        }
    }
})

export const { setInputValue, setInputValueId } = SearchSlice.actions;