import * as React from 'react';
import './App.css';
import SearchModal from './components/SearchModal/SearchModal';
import useModal from './components/SearchModal/showModal';

function App() {
  const {isOpen, toggle} = useModal()

  return (
    <div className="App">
      <button onClick={toggle}>Show Modal</button>
      <SearchModal isOpen={isOpen} toggle={toggle}></SearchModal>
    </div>
  );
}

export default App;
