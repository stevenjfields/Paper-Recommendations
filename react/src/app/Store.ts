import { configureStore } from "@reduxjs/toolkit";
import { openAlexApi } from "./OpenAlexAPI";
import { SearchSlice } from "../features/search/SearchSlice";
import { VisualizationSlice } from "../features/visualization/VisualizationSlice";

export const store = configureStore({
    reducer: {
        [openAlexApi.reducerPath]: openAlexApi.reducer,
        [SearchSlice.name]: SearchSlice.reducer,
        [VisualizationSlice.name]: VisualizationSlice.reducer
    },
    middleware: (getDefaultMiddleware) =>
      // adding the api middleware enables caching, invalidation, polling and other features of `rtk-query`
      getDefaultMiddleware().concat(openAlexApi.middleware)
  });

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch