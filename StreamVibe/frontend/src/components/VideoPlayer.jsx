import React, { useRef, useEffect, useState } from 'react';
import videojs from 'video.js';
import 'video.js/dist/video-js.css';
import '@videojs/http-streaming';

export default function VideoPlayer({ videoUrl }) {
    const videoRef = useRef(null);
    const playerRef = useRef(null);
    const [brightness, setBrightness] = useState(100);
    const [quality, setQuality] = useState('1080');

    useEffect(() => {
        // Create the video element dynamically to avoid React Strict Mode lifecycle issues
        if (!playerRef.current && videoRef.current && videoUrl) {
            const videoElement = document.createElement("video-js");
            videoElement.classList.add('vjs-big-play-centered');
            videoRef.current.appendChild(videoElement);

            // Set initial resolution based on default quality
            const hlsUrl = quality === 'auto'
                ? `${videoUrl}/ik-master.m3u8?tr=sr-240_360_480_720_1080`
                : `${videoUrl}/${quality}p-pl.m3u8?tr=sr-240_360_480_720_1080`;

            playerRef.current = videojs(videoElement, {
                controls: true,
                responsive: true,
                fluid: true,
                html5: {
                    hls: {
                        overrideNative: true
                    },
                    vhs: {
                        overrideNative: true
                    }
                },
                sources: [{ src: hlsUrl, type: 'application/x-mpegURL' }]
            });
        }

        return () => {
            if (playerRef.current) {
                playerRef.current.dispose();
                playerRef.current = null;
            }
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [videoUrl]); // Intentionally exclude 'quality' to avoid full re-initialization

    // Handle dynamic quality changes
    useEffect(() => {
        if (playerRef.current && videoUrl) {
            const hlsUrl = quality === 'auto'
                ? `${videoUrl}/ik-master.m3u8?tr=sr-240_360_480_720_1080`
                : `${videoUrl}/${quality}p-pl.m3u8?tr=sr-240_360_480_720_1080`;

            const currentSrc = playerRef.current.src();

            // Compare URLs to prevent redundant reloading
            const parser1 = document.createElement('a');
            const parser2 = document.createElement('a');
            parser1.href = currentSrc || '';
            parser2.href = hlsUrl;

            if (parser1.href !== parser2.href && currentSrc) {
                const currentTime = playerRef.current.currentTime();
                const isPaused = playerRef.current.paused();

                playerRef.current.src({ src: hlsUrl, type: 'application/x-mpegURL' });

                playerRef.current.one('loadedmetadata', () => {
                    playerRef.current.currentTime(currentTime);
                    if (!isPaused) {
                        playerRef.current.play();
                    }
                });
            }
        }
    }, [quality, videoUrl]);

    return (
        <div style={{ width: '100%' }}>
            <div style={{ aspectRatio: '16/9', width: '100%', backgroundColor: '#000', filter: `brightness(${brightness}%)`, transition: 'filter 0.3s ease' }}>
                <div data-vjs-player style={{ height: '100%' }} ref={videoRef}>
                </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 'var(--space-4)', padding: 'var(--space-4)', backgroundColor: 'var(--color-bg-secondary)', borderTop: '1px solid var(--color-border)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                    <label htmlFor="quality-select" style={{ color: 'var(--color-text-secondary)', fontWeight: 'var(--font-weight-medium)', fontSize: 'var(--font-size-sm)' }}>Quality</label>
                    <select
                        id="quality-select"
                        value={quality}
                        onChange={(e) => setQuality(e.target.value)}
                        style={{ padding: 'var(--space-2) var(--space-3)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', backgroundColor: 'var(--color-bg-primary)', color: 'var(--color-text-primary)', cursor: 'pointer', outline: 'none', fontWeight: 'var(--font-weight-medium)' }}
                    >
                        <option value="auto">Auto</option>
                        <option value="1080">1080p</option>
                        <option value="720">720p</option>
                        <option value="480">480p</option>
                        <option value="360">360p</option>
                        <option value="240">240p</option>
                    </select>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', flex: 1, minWidth: '200px', paddingLeft: 'var(--space-4)', borderLeft: '1px solid var(--color-border)' }}>
                    <label htmlFor="brightness-slider" style={{ color: 'var(--color-text-secondary)', fontWeight: 'var(--font-weight-medium)', fontSize: 'var(--font-size-sm)' }}>Brightness</label>
                    <input
                        id="brightness-slider"
                        type="range"
                        min="50"
                        max="150"
                        value={brightness}
                        onChange={(e) => setBrightness(e.target.value)}
                        style={{ flex: 1, cursor: 'pointer', accentColor: 'var(--color-accent)' }}
                    />
                    <span style={{ color: 'var(--color-text-primary)', minWidth: '45px', textAlign: 'right', fontWeight: 'var(--font-weight-bold)' }}>{brightness}%</span>
                </div>
            </div>
        </div>
    );
}
