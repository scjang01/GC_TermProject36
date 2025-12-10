import json
#플레이리스트 load
def load_playlist(file_path="playlist.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def recommend_music(emotion, playlist_data):
    # 감정이 플레이리스트에 있으면 그 목록 반환
    if emotion in playlist_data:
        return playlist_data[emotion]
    else:
        return ["No playlist found for this emotion."]
