import openai
from django.conf import settings

# 新 SDK 初始化 client
client = openai.OpenAI(api_key=settings.GPT_API_KEY)

def generate_event_report_with_gpt(event_data, responses_summary):
    prompt = f"""
你是一位專業活動助理，請根據以下活動資訊撰寫一份繁體中文的活動結案報告，內容包含：

1. 活動簡介（請根據提供的活動名稱、時間、地點、類型簡要描述活動）
2. 執行情況（請根據報名人數與實到人數簡單分析出席狀況）
3. 參與者回饋（列出所有回答，僅根據提供的問卷摘要撰寫，若問卷資料不足請簡述「尚無完整統計資料」）
4. 建議與反思（請避免虛構資料，僅提出通用或可推論的改善建議）

活動資料如下：

活動名稱：{event_data['name']}
活動時間：{event_data['event_time']}
活動地點：{event_data['location']}
活動類型：{event_data['activity_type']}
語言：{event_data['language']}
報名人數：{event_data['registrations']}
實到人數：{event_data['attendees']}
問卷摘要如下：
{responses_summary or "目前尚無問卷資料"}
"""

    try:
        response = client.chat.completions.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
)

        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 報告生成失敗：{str(e)}"
