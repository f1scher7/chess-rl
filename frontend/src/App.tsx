import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/home/Home';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import ChessBoardPage from './pages/chessBoardPage/ChessBoardPage';


function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/agents-play" element={<ChessBoardPage isView={true} />} />
                <Route path="/user-play" element={<ChessBoardPage isView={false} />} />
            </Routes>
        </Router>
    );
}

export default App;
