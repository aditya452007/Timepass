import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { searchVideos } from '../api';
import VideoCard from '../components/VideoCard';

export default function Search() {
    const [searchParams] = useSearchParams();
    const q = searchParams.get('q') || '';

    const [videos, setVideos] = useState([]);
    const [page, setPage] = useState(1);
    const [loading, setLoading] = useState(false);
    const [hasMore, setHasMore] = useState(true);

    const fetchResults = async (query, pageNum, append = false) => {
        try {
            setLoading(true);
            const data = await searchVideos(query, pageNum);
            if (append) {
                setVideos(prev => [...prev, ...(data.videos || [])]);
            } else {
                setVideos(data.videos || []);
            }
            setHasMore(data.currentPage < data.totalPages);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        setPage(1);
        fetchResults(q, 1, false);
    }, [q]);

    return (
        <div className="page-container">
            <h2 style={{ marginBottom: 'var(--space-5)' }}>
                Search results for "{q}"
            </h2>

            {videos?.length === 0 && !loading && <p>No results found for "{q}".</p>}

            <div className="video-grid">
                {videos?.map(video => (
                    <VideoCard key={video._id} video={video} />
                ))}
            </div>

            {loading && <p style={{ textAlign: 'center', margin: 'var(--space-5)' }}>Loading...</p>}

            {hasMore && !loading && (
                <div style={{ textAlign: 'center', marginTop: 'var(--space-5)' }}>
                    <button className="btn-ghost" onClick={() => {
                        const nextPage = page + 1;
                        setPage(nextPage);
                        fetchResults(q, nextPage, true);
                    }}>
                        Load More
                    </button>
                </div>
            )}
        </div>
    );
}
