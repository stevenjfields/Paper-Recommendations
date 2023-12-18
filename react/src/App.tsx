import './App.css'
import LoadingScreen from './features/loading-screen/LoadingScreen';
import type { RootState } from './app/Store';
import { useAppSelector, useAppDispatch } from './app/Hooks';
import { useAutocompleteQuery } from './app/OpenAlexAPI';
import Visualization from './features/visualization/Visualization';



export default function App() {
  const selector = useAppSelector;
  const input_value = selector((state: RootState) => state.search.input_value)
  const loading = selector((state: RootState) => state.visualization.loading);

  const {data, error, isLoading} = useAutocompleteQuery(input_value)
  return (
      loading ?
      <LoadingScreen /> :
      <Visualization />
  )
}
