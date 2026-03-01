import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getProfile, followUser } from '../api';
import VideoCard from '../components/VideoCard';
import { useAuth } from '../context/AuthContext';

export default function Profile() {
    const { username } = useParams();
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const { user } = useAuth();
    const [isFollowingLocally, setIsFollowingLocally] = useState(false);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                setLoading(true);
                const data = await getProfile(username);
                setProfile(data);
                if (user && user.following?.includes(data._id)) {
                    setIsFollowingLocally(true);
                } else {
                    setIsFollowingLocally(false);
                }
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, [username, user]);

    const handleFollow = async () => {
        try {
            const res = await followUser(profile._id);
            setIsFollowingLocally(res.following);
            setProfile(prev => ({
                ...prev,
                followerCount: res.followerCount
            }));
        } catch (err) {
            console.error(err);
        }
    };

    if (loading) return <div className="page-container"><p>Loading...</p></div>;
    if (!profile) return <div className="page-container"><p>Profile not found.</p></div>;

    const isOwnProfile = user && user._id === profile._id;

    return (
        <div className="page-container">
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-6)', marginBottom: 'var(--space-8)' }}>
                <div className="avatar" style={{ width: '80px', height: '80px', fontSize: 'var(--font-size-xl)' }}>
                    {profile.username.charAt(0)}
                </div>
                <div>
                    <h1 style={{ marginBottom: 'var(--space-2)' }}>{profile.username}</h1>
                    <div style={{ color: 'var(--color-text-secondary)', display: 'flex', gap: 'var(--space-4)', marginBottom: 'var(--space-3)' }}>
                        <span><strong>{profile.followerCount}</strong> followers</span>
                        <span><strong>{profile.followingCount}</strong> following</span>
                    </div>
                    {!isOwnProfile && user && (
                        <button className={isFollowingLocally ? 'btn-ghost' : 'btn-primary'} onClick={handleFollow}>
                            {isFollowingLocally ? 'Unfollow' : 'Follow'}
                        </button>
                    )}
                    {!user && (
                        <button className="btn-primary" disabled>Login to Follow</button>
                    )}
                </div>
            </div>

            <h2 style={{ marginBottom: 'var(--space-4)', borderBottom: '1px solid var(--color-border)', paddingBottom: 'var(--space-2)' }}>
                Videos
            </h2>

            {profile.videos?.length === 0 ? (
                <p>This user hasn't uploaded any videos yet.</p>
            ) : (
                <div className="video-grid">
                    {profile.videos?.map(video => (
                        <VideoCard key={video._id} video={video} />
                    ))}
                </div>
            )}
        </div>
    );
}
