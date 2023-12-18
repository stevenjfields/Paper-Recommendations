import { configureStore } from "@reduxjs/toolkit";
import { openAlexApi } from "./OpenAlexAPI";
import { SearchSlice } from "../features/search/SearchSlice";
import { VisualizationSlice } from "../features/visualization/VisualizationSlice";
import { paperRecommendationsAPI } from "./PaperRecommendationsAPI";

export const store = configureStore({
    reducer: {
        [openAlexApi.reducerPath]: openAlexApi.reducer,
        [paperRecommendationsAPI.reducerPath]: paperRecommendationsAPI.reducer,
        [SearchSlice.name]: SearchSlice.reducer,
        [VisualizationSlice.name]: VisualizationSlice.reducer
    },
    middleware: (getDefaultMiddleware) =>
      // adding the api middleware enables caching, invalidation, polling and other features of `rtk-query`
      getDefaultMiddleware().concat(openAlexApi.middleware).concat(paperRecommendationsAPI.middleware)
  });

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch