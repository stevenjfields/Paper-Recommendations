import { useState } from 'react'
import './App.css'
import LoadingScreen from './features/loading-screen/LoadingScreen';
import type { RootState } from './app/Store';
import { useAppSelector, useAppDispatch } from './app/Hooks';
import { useAutocompleteQuery } from './app/OpenAlexAPI';
import Search from './features/search/Search';



export default function App() {
  const selector = useAppSelector;
  const dispatch = useAppDispatch;
  const input_value = selector((state: RootState) => state.search.input_value)

  const {data, error, isLoading} = useAutocompleteQuery(input_value)
  return (
      isLoading ?
      <LoadingScreen /> :
      <div>
        <Search />
      </div>
  )
}
