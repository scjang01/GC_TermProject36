import gradio as gr
from analyzer import EmotionAnalyzer
from recommender import load_playlist, recommend_music

# 감정별 이모지 매핑
emotion_emoji = {
    'joy': '😄',
    'sadness': '😢', 
    'anger': '😠',
    'fear': '😨',
    'surprise': '😮',
    'disgust': '🤢',
    'neutral': '😐'
}

print("=" * 50)
print("🎵 Emotion-based Music Recommender Starting")
print("=" * 50)
print("Loading models and data... Please wait a moment.")

try:
    analyzer = EmotionAnalyzer()       # 감정 분석 모델 로드
    playlist_data = load_playlist()    # 플레이리스트 데이터 로드
    print("Loading complete! Starting web app.")
except Exception as e:
    print(f"Initialization error: {str(e)}")
    exit(1)

# 분석 및 추천
def analyze_and_recommend(text):
    
    # 입력값 검증
    if not text.strip():
        return "**Please enter some text.**\n\nFeel free to describe your feelings or situation in English!"
    
    try:
        # 감정 분석
        analysis_result = analyzer.analyze_paragraph(text)
        detected_emotion = analysis_result['final_emotion']
        confidence_scores = analysis_result['weighted_scores']
        
        # 음악 추천
        recommendations = recommend_music(detected_emotion, playlist_data)
        
        # 결과 메시지 구성
        emoji = emotion_emoji.get(detected_emotion, '🎭')
        
        result_msg = f"## {emoji} Emotion Analysis Result\n\n"
        result_msg += f"**Detected Emotion:** {detected_emotion.upper()}\n"
        result_msg += f"**Confidence:** {confidence_scores[detected_emotion]:.2%}\n\n"
        
        result_msg += f"---\n\n"
        result_msg += f"### 🎵 Recommended playlist for '{detected_emotion}' emotion\n\n"
        
        if isinstance(recommendations, list) and len(recommendations) > 0:
            for i, url in enumerate(recommendations, 1):
                if url != "No playlist found for this emotion.":
                    result_msg += f"{i}. [Click to Listen on YouTube]({url})\n"
                else:
                    result_msg += f"⚠️ {url}\n"
        else:
            result_msg += "No recommended music available.\n"
            
        # 막대 그래프 시각화
        result_msg += f"\n---\n\n"
        result_msg += f"### 📊 Detailed Emotion Analysis\n"
        sorted_emotions = sorted(confidence_scores.items(), key=lambda x: x[1], reverse=True)
        for emotion, score in sorted_emotions[:3]:  # 상위 3개만 표시
            bar = "█" * int(score * 20)  # 텍스트로 막대바 구현
            result_msg += f"**{emotion}**: {score:.1%} {bar}\n"
        
        return result_msg
        
    except Exception as e:
        error_msg = f"**An error occurred during analysis**\n\n"
        error_msg += f"Error details: {str(e)}\n\n"
        error_msg += f"Please try again with different text."
        return error_msg

# Gradio 인터페이스
def create_interface():
    
    iface = gr.Interface(
        fn=analyze_and_recommend,
        inputs=gr.Textbox(
            lines=6,
            placeholder="Enter a sentence and describe your feelings or mood...\nExample: 'I am so happy today! Everything went perfectly.'\nOr: 'I feel so sad and need some comfort.'",
            label="Your Story",
            info="Please input text in English for accurate analysis." # 영어 입력 권장
        ),
        outputs=gr.Markdown(
            label="Analysis Result & Recommended Music"
        ),
        title="Emotion-based Music Recommender",
        description="""
        **Enter a sentence in English and get music suggestions based on your emotion!**
        
        📝 Text Input → 🤖 Emotion Analysis → 🎵 Music Recommendation → 🎧 Listen Now
        """,
        examples=[
            ["I am so happy today! Everything is wonderful and I feel amazing!"],
            ["I feel so sad and lonely. I need some comfort and peaceful music."],
            ["The movie was terrifying but exciting. My heart is still beating fast!"],
        ],
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        """,
        allow_flagging="never"
    )
    
    return iface

# 메인 실행
if __name__ == "__main__":
    print("🌐 Starting Gradio web server...")
    
    interface = create_interface()
    
    interface.launch(
        server_name="127.0.0.1",  # 윈도우 방화벽 문제 방지
        server_port=7860,       
        share=False,           
        debug=True,             # 에러 확인을 위해 디버그 모드 켬
        show_error=True         
    )