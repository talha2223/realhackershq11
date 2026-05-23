import React, { useRef, useState, useEffect } from 'react';
import { Volume2, VolumeX } from 'lucide-react';
import { useLoading } from './LoadingContext';

const BackgroundVideo: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isMuted, setIsMuted] = useState(true);
  const { setVideoLoaded } = useLoading();

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.oncanplaythrough = () => {
        setVideoLoaded();
      };
    }
  }, [setVideoLoaded]);

  const toggleMute = () => {
    if (audioRef.current) {
      const newMutedState = !isMuted;
      audioRef.current.muted = newMutedState;
      
      // If unmuting, try to play if not already playing (browsers block auto-play audio)
      if (!newMutedState) {
        audioRef.current.play().catch(e => console.error("Audio play failed:", e));
      }
      
      setIsMuted(newMutedState);
    }
  };

  return (
    <>
      <video
        ref={videoRef}
        autoPlay
        loop
        muted
        playsInline
        className="background-video"
      >
        <source src="/assets/backgroud.webm" type="video/webm" />
        Your browser does not support the video tag.
      </video>
      
      {/* External Background Audio */}
      <audio
        ref={audioRef}
        src="/assets/videoplayback.weba"
        loop
        muted={isMuted}
        autoPlay
      />

      <button className="unmute-btn" onClick={toggleMute} title={isMuted ? "Unmute" : "Mute"}>
        {isMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
      </button>
    </>
  );
};

export default BackgroundVideo;
