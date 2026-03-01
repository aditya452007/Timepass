import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { getVideo, incrementView, toggleLike } from '../api';
import VideoPlayer from '../components/VideoPlayer';
import { useAuth } from '../context/AuthContext';

export default function Watch() {
    const { videoId } = useParams();
    const [video, setVideo] = useState(null);
    const [loading, setLoading] = useState(true);
    const { user } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        let viewIncremented = false;
        const fetchAndTrack = async () => {
            try {
                setLoading(true);
                const data = await getVideo(videoId);
                setVideo(data);
                if (!viewIncremented) {
                    viewIncremented = true;
                    incrementView(videoId);
                }
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchAndTrack();
    }, [videoId]);

    const handleLike = async () => {
        if (!user) {
            navigate('/login');
            return;
        }
        try {
            const res = await toggleLike(videoId);
            setVideo(prev => ({
                ...prev,
                likes: res.liked
                    ? [...prev.likes, user._id]
                    : prev.likes.filter(id => id !== user._id)
            }));
        } catch (err) {
            console.error(err);
        }
    };

    if (loading) return <div className="page-container"><p>Loading...</p></div>;
    if (!video) return <div className="page-container"><p>Video not found.</p></div>;

    const isLiked = user && video.likes?.includes(user._id);

    return (
        <div className="page-container" style={{ maxWidth: 'var(--max-width)', padding: '0 var(--space-4) var(--space-8)' }}>
            <div style={{ background: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-lg)', overflow: 'hidden', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)' }}>
                <VideoPlayer videoUrl={video.imagekitUrl} />
            </div>

            <div style={{ marginTop: 'var(--space-6)', maxWidth: '1000px', margin: 'var(--space-6) auto 0' }}>
                <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 'var(--font-weight-bold)', marginBottom: 'var(--space-3)', letterSpacing: '-0.5px' }}>
                    {video.title}
                </h1>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--color-border)', paddingBottom: 'var(--space-4)', marginBottom: 'var(--space-5)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
                        <Link to={`/profile/${video.uploader?.username}`}>
                            <div className="avatar" style={{ width: '48px', height: '48px', fontSize: 'var(--font-size-md)' }}>
                                {video.uploader?.username?.charAt(0) || 'U'}
                            </div>
                        </Link>
                        <div>
                            <Link to={`/profile/${video.uploader?.username}`} style={{ fontWeight: 'var(--font-weight-bold)', fontSize: 'var(--font-size-md)', display: 'block', color: 'var(--color-text-primary)' }}>
                                {video.uploader?.username}
                            </Link>
                            <span style={{ color: 'var(--color-text-muted)', fontSize: 'var(--font-size-sm)' }}>
                                {video.viewCount + 1} views
                            </span>
                        </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-5)' }}>
                        <button
                            className={`btn-ghost ${isLiked ? 'liked' : ''}`}
                            onClick={handleLike}
                            style={{
                                color: isLiked ? 'var(--color-accent)' : 'inherit',
                                borderColor: isLiked ? 'var(--color-accent)' : 'var(--color-border)',
                                display: 'flex', gap: 'var(--space-2)', alignItems: 'center'
                            }}
                        >
                            <span style={{ fontSize: '1.2em' }}>{isLiked ? '♥' : '♡'}</span> {video.likes?.length || 0}
                        </button>
                    </div>
                </div>

                <div style={{ backgroundColor: 'var(--color-bg-secondary)', padding: 'var(--space-5)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--color-border)' }}>
                    <p style={{ marginBottom: 'var(--space-4)', whiteSpace: 'pre-wrap', lineHeight: '1.8', color: 'var(--color-text-primary)' }}>{video.description}</p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
                        {video.tags?.map((tag, i) => (
                            <span key={i} className="tag-chip">#{tag}</span>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
