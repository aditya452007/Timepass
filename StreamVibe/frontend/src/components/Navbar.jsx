import React, { useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
    const { user, logout } = useAuth();
    const searchRef = useRef(null);
    const navigate = useNavigate();

    const handleSearch = (e) => {
        e.preventDefault();
        if (searchRef.current?.value) {
            navigate(`/search?q=${encodeURIComponent(searchRef.current.value)}`);
        }
    };

    return (
        <nav className="navbar">
            <Link to="/" className="logo">StreamVibe</Link>
            <form onSubmit={handleSearch} className="search-form">
                <input
                    type="text"
                    ref={searchRef}
                    placeholder="Search videos..."
                    className="search-input"
                />
            </form>
            <div style={{ display: 'flex', gap: 'var(--space-4)', alignItems: 'center' }}>
                {user ? (
                    <>
                        <Link to="/upload" className="btn-primary" style={{ padding: 'var(--space-1) var(--space-3)' }}>Upload</Link>
                        <Link to={`/profile/${user?.username}`}>
                            <div className="avatar">
                                {user?.username?.charAt(0)?.toUpperCase() || 'U'}
                            </div>
                        </Link>
                        <button onClick={logout} className="btn-ghost" style={{ padding: 'var(--space-1) var(--space-3)' }}>Logout</button>
                    </>
                ) : (
                    <>
                        <Link to="/login" className="btn-ghost" style={{ padding: 'var(--space-1) var(--space-3)' }}>Login</Link>
                        <Link to="/register" className="btn-primary" style={{ padding: 'var(--space-1) var(--space-3)' }}>Register</Link>
                    </>
                )}
            </div>
        </nav>
    );
}
