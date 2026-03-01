import React from 'react';
import { Link } from 'react-router-dom';

export default function VideoCard({ video }) {
    if (!video) return null;

    return (
        <div className="video-card">
            <Link to={`/watch/${video._id}`}>
                {video.thumbnailUrl ? (
                    <img src={video.thumbnailUrl} alt={video.title} />
                ) : (
                    <div style={{ width: '100%', aspectRatio: '16/9', backgroundColor: 'var(--color-bg-hover)' }}></div>
                )}
            </Link>
            <div className="card-body">
                <Link to={`/watch/${video._id}`} className="title">
                    {video.title}
                </Link>
                <div className="meta">
                    <Link to={`/profile/${video.uploader?.username}`} style={{ color: 'inherit' }}>
                        {video.uploader?.username || 'Unknown'}
                    </Link>
                    <span>{video.viewCount || 0} views</span>
                </div>
            </div>
        </div>
    );
}
