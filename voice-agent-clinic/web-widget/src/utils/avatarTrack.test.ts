import { describe, expect, it } from "vitest";
import { selectRemoteAvatarVideoTrack } from "./avatarTrack";

describe("selectRemoteAvatarVideoTrack", () => {
  it("never returns the local camera", () => {
    const local = {} as MediaStreamTrack;
    const remote = {} as MediaStreamTrack;
    expect(selectRemoteAvatarVideoTrack({
      local: { local: true, tracks: { camera: { kind: "video", track: local } } },
      avatar: { local: false, tracks: { video: { kind: "video", track: remote } } },
    })).toBe(remote);
  });

  it("returns null while a remote video track is unavailable", () => {
    expect(selectRemoteAvatarVideoTrack({ avatar: { local: false, tracks: { video: { kind: "video", track: null } } } })).toBeNull();
  });
});
