import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { login as apiLogin } from '../api';

export default function Login() {
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
            const data = await apiLogin({ email, password });
            login(data.user);
            navigate('/');
        } catch (err) {
            setError(err.response?.data?.error || 'Login failed');
        }
    };

    return (
        <div className="auth-card">
            <h1>Login</h1>
            <form onSubmit={handleSubmit}>
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
                <button type="submit" className="btn-primary" style={{ width: '100%' }}>Login</button>
            </form>
            <p style={{ marginTop: 'var(--space-4)', textAlign: 'center' }}>
                Don't have an account? <Link to="/register" style={{ color: 'var(--color-accent)' }}>Register</Link>
            </p>
        </div>
    );
}
