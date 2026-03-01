import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { getUploadAuth, createVideo } from '../api';

export default function Upload() {
    const { user } = useAuth();
    const navigate = useNavigate();

    const [file, setFile] = useState(null);
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [tags, setTags] = useState('');
    const [progress, setProgress] = useState(0);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState('');
    const [newVideoId, setNewVideoId] = useState(null);

    useEffect(() => {
        if (!user) navigate('/login?next=/upload');
    }, [user, navigate]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file || !title) {
            setError('File and Title are required');
            return;
        }
        setError('');
        setUploading(true);
        setProgress(0);

        try {
            const authParams = await getUploadAuth();

            const formData = new FormData();
            formData.append('file', file);
            formData.append('fileName', file.name);
            formData.append('publicKey', authParams.publicKey);
            formData.append('signature', authParams.signature);
            formData.append('expire', authParams.expire);
            formData.append('token', authParams.token);
            formData.append('folder', '/videos');

            const ikRes = await axios.post('https://upload.imagekit.io/api/v1/files/upload', formData, {
                onUploadProgress: (progressEvent) => {
                    const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    setProgress(percent);
                }
            });

            const videoData = {
                title,
                description,
                tags: tags.split(',').map(t => t.trim()).filter(Boolean),
                imagekitFileId: ikRes.data.fileId,
                imagekitUrl: ikRes.data.url,
                thumbnailUrl: ikRes.data.thumbnailUrl || (ikRes.data.url + '/ik-thumbnail.jpg')
            };

            const newVideo = await createVideo(videoData);
            setNewVideoId(newVideo._id);
        } catch (err) {
            setError(err.response?.data?.error || err.message || 'Upload failed');
        } finally {
            setUploading(false);
        }
    };

    if (newVideoId) {
        return (
            <div className="page-container" style={{ textAlign: 'center', marginTop: 'var(--space-10)' }}>
                <h2>Upload Complete!</h2>
                <br />
                <Link to={`/watch/${newVideoId}`} className="btn-primary">Watch Your Video</Link>
            </div>
        );
    }

    return (
        <div className="auth-card" style={{ maxWidth: '600px' }}>
            <h1 style={{ marginBottom: 'var(--space-4)' }}>Upload Video</h1>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label>Video File (MP4)</label>
                    <input
                        type="file"
                        accept=".mp4"
                        onChange={(e) => setFile(e.target.files[0])}
                        className="form-input"
                        required
                        disabled={uploading}
                    />
                </div>
                <div className="form-group">
                    <label>Title</label>
                    <input
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        className="form-input"
                        required
                        disabled={uploading}
                    />
                </div>
                <div className="form-group">
                    <label>Description (Optional)</label>
                    <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        className="form-input"
                        rows={4}
                        disabled={uploading}
                    />
                </div>
                <div className="form-group">
                    <label>Tags (comma separated)</label>
                    <input
                        type="text"
                        value={tags}
                        onChange={(e) => setTags(e.target.value)}
                        className="form-input"
                        disabled={uploading}
                    />
                </div>

                {error && <span className="form-error">{error}</span>}

                <button type="submit" className="btn-primary" disabled={uploading} style={{ width: '100%' }}>
                    {uploading ? 'Uploading...' : 'Upload'}
                </button>

                {uploading && (
                    <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${progress}%` }} />
                    </div>
                )}
            </form>
        </div>
    );
}
