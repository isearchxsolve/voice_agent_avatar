export type VideoTrackLike = {
  kind?: string;
  track?: MediaStreamTrack | null;
};

export type ParticipantLike = {
  local?: boolean;
  tracks?: Record<string, VideoTrackLike>;
};

/** Select the first usable remote/avatar video track, never a local camera. */
export function selectRemoteAvatarVideoTrack(
  participants: Record<string, ParticipantLike> | undefined,
): MediaStreamTrack | null {
  if (!participants) return null;
  for (const participant of Object.values(participants)) {
    if (participant.local) continue;
    for (const candidate of Object.values(participant.tracks ?? {})) {
      if (candidate.kind === "video" && candidate.track) return candidate.track;
    }
  }
  return null;
}
