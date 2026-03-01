import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { register as apiRegister } from '../api';

export default function Register() {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { user, login } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        if (user) navigate('/');
    }, [user, navigate]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            const data = await apiRegister({ username, email, password });
            login(data.user);
            navigate('/');
        } catch (err) {
            setError(err.response?.data?.error || 'Registration failed');
        }
    };

    return (
        <div className="auth-card">
            <h1>Register</h1>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label>Username</label>
                    <input
                        type="text"
                        className="form-input"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Email</label>
                    <input
                        type="email"
                        className="form-input"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Password</label>
                    <input
                        type="password"
                        className="form-input"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                {error && <span className="form-error">{error}</span>}
                <button type="submit" className="btn-primary" style={{ width: '100%' }}>Register</button>
            </form>
            <p style={{ marginTop: 'var(--space-4)', textAlign: 'center' }}>
                Already have an account? <Link to="/login" style={{ color: 'var(--color-accent)' }}>Login</Link>
            </p>
        </div>
    );
}
