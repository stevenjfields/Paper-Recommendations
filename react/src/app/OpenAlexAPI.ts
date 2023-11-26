import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const openAlexApi = createApi({
    reducerPath: "openAlexApi",
    baseQuery: fetchBaseQuery({baseUrl: "https://api.openalex.org/"}),
    endpoints: (builder) => ({
        autocomplete: builder.query({
            query: (input: string) => `autocomplete/works?q=${input}`,
        }),
    }),
})

export const { useAutocompleteQuery } = openAlexApi