import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export interface PaperDetails {
    work_id: string,
    title: string,
    landing_page_url: string,
    inverted_abstract: Map<string, Array<number>> | null,
    authors: Array<string>,
    institutions: Array<string>,
    concepts: Array<string>,
    referenced_works: Array<string>,
    related_works: Array<string>
}

export interface WeightedEdge {
    target: string,
    source: string,
    weight: number,
    root_weight: number,
    concept_overlap: number,
    author_overlap: number
}

export interface GetSimilarityPayload {
    root: PaperDetails,
    target: PaperDetails,
    sources: PaperDetails
}

export const paperRecommendationsAPI = createApi({
    reducerPath: "paperRecommendationsAPI",
    baseQuery: fetchBaseQuery({baseUrl: "http://0.0.0.0:8080/"}),
    endpoints: (builder) => ({
        fetchRootPaper: builder.query({
            query: (work_id: string) => `paper/${work_id}/`
        }),
        fetchReferences: builder.query({
            query: (work: PaperDetails) => ({
                url: `references/`,
                method: "POST",
                body: work
            })
        }),
        createEmbeddings: builder.query({
            query: (works: Array<PaperDetails>) => ({
                url: `embeddings/`,
                method: "POST",
                body: works
            })
        }),
        getSimilarities: builder.query({
            query: (data: GetSimilarityPayload) => ({
                url: `similarities/`,
                method: "POST",
                body: data
            })
        })    
    })
})

export const { useFetchRootPaperQuery, useFetchReferencesQuery, useCreateEmbeddingsQuery, useGetSimilaritiesQuery } = paperRecommendationsAPI