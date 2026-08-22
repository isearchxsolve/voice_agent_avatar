import React, { useEffect, useRef, useState } from "react";
import { DailyProvider, useDaily } from "@daily-co/daily-react";
import { useHeyGenStream } from "../utils/heygen";
import { selectRemoteAvatarVideoTrack } from "../utils/avatarTrack";
import "../styles/widget.css";

interface AvatarWidgetProps {
  roomUrl: string;
  token: string;
  avatarId?: string;
  onClose?: () => void;
  showBooking?: boolean;
}

const AvatarWidgetInner: React.FC<AvatarWidgetProps> = ({ roomUrl, token, onClose, showBooking = true }) => {
  const daily = useDaily();
  const videoRef = useRef<HTMLVideoElement>(null);
  const [status, setStatus] = useState<"connecting" | "connected" | "disconnected" | "error">("connecting");
  const [showControls, setShowControls] = useState(true);

  const { startSession, stopSession, isStreaming } = useHeyGenStream();

  useEffect(() => {
    if (!daily) return;
    daily.join({ url: roomUrl, token }).catch((err) => {
      console.error("Join error:", err);
      setStatus("error");
    });

    const syncRemoteVideo = () => {
      const remoteTrack = selectRemoteAvatarVideoTrack(daily.participants());
      if (videoRef.current && remoteTrack) videoRef.current.srcObject = new MediaStream([remoteTrack]);
    };
    daily.on("joined-meeting", () => { setStatus("connected"); syncRemoteVideo(); });
    daily.on("participant-joined", syncRemoteVideo);
    daily.on("track-started", syncRemoteVideo);
    daily.on("left-meeting", () => setStatus("disconnected"));
    daily.on("error", () => setStatus("error"));

    return () => {
      daily.off("participant-joined", syncRemoteVideo);
      daily.off("track-started", syncRemoteVideo);
      daily.leave();
    };
  }, [daily, roomUrl, token]);

  useEffect(() => {
    if (!videoRef.current || !daily) return;

    const remoteTrack = selectRemoteAvatarVideoTrack(daily.participants());
    if (remoteTrack) videoRef.current.srcObject = new MediaStream([remoteTrack]);
  }, [daily, status]);

  const handleMicToggle = () => {
    if (!daily) return;
    daily.setLocalAudio(!daily.localAudio());
  };

  const handleCameraToggle = () => {
    if (!daily) return;
    daily.setLocalVideo(!daily.localVideo());
  };

  const handleLeave = () => {
    if (!daily) return;
    daily.leave();
    stopSession();
    onClose?.();
  };

  const handleStartAvatar = async () => {
    await startSession();
  };

  const handleStopAvatar = () => {
    stopSession();
  };

  const toggleControls = () => {
    setShowControls((prev) => !prev);
  };

  return (
    <div className="avatar-widget-container">
      <div className="avatar-widget-header">
        <span className="avatar-widget-title">AI Assistant</span>
        <div className="avatar-widget-status">
          <span className={`status-dot status-${status}`} />
          {status}
        </div>
        <button className="avatar-widget-close" onClick={handleLeave} aria-label="Close">
          ×
        </button>
      </div>

      <div className="avatar-widget-video" onClick={toggleControls}>
        <video ref={videoRef} autoPlay playsInline muted className="avatar-video" />
        {status === "connecting" && (
          <div className="avatar-loading">
            <div className="spinner" />
            <p>Connecting to AI assistant...</p>
          </div>
        )}
      </div>

      {showControls && (
        <div className="avatar-widget-controls">
          <button onClick={handleMicToggle} className="control-btn" aria-label="Toggle microphone">
            🎤
          </button>
          <button onClick={handleCameraToggle} className="control-btn" aria-label="Toggle camera">
            📹
          </button>
          <button
            onClick={isStreaming ? handleStopAvatar : handleStartAvatar}
            className={`control-btn ${isStreaming ? "active" : ""}`}
            aria-label="Toggle avatar"
          >
            🤖
          </button>
          <button onClick={handleLeave} className="control-btn control-btn-end" aria-label="End call">
            📞
          </button>
        </div>
      )}

      {showBooking && status === "connected" && (
        <div className="avatar-widget-booking">
          <button className="booking-btn" onClick={() => alert("Booking integration coming soon!")}>
            📅 Book Appointment
          </button>
        </div>
      )}
    </div>
  );
};

export const AvatarWidget: React.FC<AvatarWidgetProps> = (props) => (
  <DailyProvider>
    <AvatarWidgetInner {...props} />
  </DailyProvider>
);

export default AvatarWidget;
