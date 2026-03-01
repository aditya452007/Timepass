import React, { useEffect, useState } from 'react';
import { getVideos } from '../api';
import VideoCard from '../components/VideoCard';

export default function Home() {
    const [videos, setVideos] = useState([]);
    const [page, setPage] = useState(1);
    const [loading, setLoading] = useState(false);
    const [hasMore, setHasMore] = useState(true);

    const fetchVideos = async (pageNum) => {
        try {
            setLoading(true);
            const data = await getVideos(pageNum);
            if (pageNum === 1) {
                setVideos(data.videos || []);
            } else {
                setVideos(prev => [...prev, ...(data.videos || [])]);
            }
            setHasMore(data.currentPage < data.totalPages);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchVideos(1);
    }, []);

    return (
        <div className="page-container">
            {/* Hero Section */}
            <div style={{
                textAlign: 'center',
                padding: 'var(--space-10) var(--space-4)',
                marginBottom: 'var(--space-8)',
                background: 'var(--color-bg-secondary)',
                borderRadius: 'var(--radius-lg)',
                border: '1px solid var(--color-border)',
                boxShadow: '0 20px 40px rgba(0,0,0,0.5)',
                position: 'relative',
                overflow: 'hidden'
            }}>
                <div style={{
                    position: 'absolute', top: '-50%', left: '-50%', width: '200%', height: '200%',
                    background: 'radial-gradient(circle at center, var(--color-accent-glow) 0%, transparent 60%)',
                    opacity: 0.15, zIndex: 0, pointerEvents: 'none'
                }}></div>
                <div style={{ position: 'relative', zIndex: 1 }}>
                    <h1 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 'var(--font-weight-bold)', marginBottom: 'var(--space-4)', letterSpacing: '-1px' }}>
                        Welcome to <span style={{ background: 'var(--color-accent-gradient)', WebkitBackgroundClip: 'text', backgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>StreamVibe</span>
                    </h1>
                    <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--font-size-lg)', maxWidth: '800px', margin: '0 auto var(--space-6)' }}>
                        A premium learning project showcasing high-performance adaptive bitrate HLS streaming, seamless ImageKit CDN integration, and stunning UI/UX designed with neon dark aesthetics.
                    </p>
                </div>
            </div>

            {videos?.length === 0 && !loading && (
                <div style={{ textAlign: 'center', padding: 'var(--space-10)', color: 'var(--color-text-muted)' }}>
                    <p>No videos available yet. Be the first to upload!</p>
                </div>
            )}
            <div className="video-grid">
                {videos?.map(video => (
                    <VideoCard key={video._id} video={video} />
                ))}
            </div>
            {loading && <p style={{ textAlign: 'center', margin: 'var(--space-5)' }}>Loading...</p>}
            {hasMore && !loading && (
                <div style={{ textAlign: 'center', marginTop: 'var(--space-5)' }}>
                    <button className="btn-ghost" onClick={() => {
                        setPage(p => p + 1);
                        fetchVideos(page + 1);
                    }}>
                        Load More
                    </button>
                </div>
            )}
        </div>
    );
}
