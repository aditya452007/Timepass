import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Upload from './pages/Upload';
import Watch from './pages/Watch';
import Profile from './pages/Profile';
import Search from './pages/Search';

function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/watch/:videoId" element={<Watch />} />
        <Route path="/profile/:username" element={<Profile />} />
        <Route path="/search" element={<Search />} />
      </Routes>
    </>
  );
}

export default App;
