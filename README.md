
# QBeep 活動管理系統

本活動管理平台根據淡江資工系友會實際需求開發，支援報名活動、簽到簽退、後台分析等功能，並整合 QR Code、回饋表單與權限管理機制，也適合校內活動、社團管理或研討會場域使用。

## 🌟 專案特色
- ✅ 將於 6 月實際應用於系友會活動，實現 POB（Proof of Business）
- 📝 提供活動報名系統，支援人數上限與報名時間限制
- 📥 使用者可註冊、登入，支援自動登入與個人資訊編輯
- 📤 報名後自動產生 QR Code，支援掃碼簽到與簽退
- 📅 管理者可新增、編輯活動資訊
- ✅ 支援活動出席紀錄、問卷填寫與回饋統計功能
- 📊 後台提供視覺化報名人數、回饋率與回覆內容分析
- 🛡️ 權限明確劃分：管理員 / 活動負責人 / 一般使用者
- 📦 全站採用 Zeabur 雲端部署，方便即時訪問與維護


## 🛠️ 技術架構

- Python 3.12
- Django 5.1.1
- SQLite
- QRCode 模組
- Zeabur 自動部署 


## 📦 本地端安裝與啟動方式

```bash
git clone https://github.com/CodingNoob1224/qbeep_final.git
cd qbeep_final/app

# 安裝依賴套件
pip install -r requirements.txt

# 遷移資料庫
python manage.py makemigrations
python manage.py migrate

# 啟動本地伺服器
python manage.py runserver 0.0.0.0:80
```

## 🧪 測試帳號

| 角色 | 帳號 | 密碼 |
|------|------|------|
| 管理員 | admin | Password001 |
| 活動負責人 | 郭佩芸 | Password001 |
| 一般使用者 | demo_01 | Password001 |

## 📁 資料夾結構簡介

```
qbeep_final/
├── app/
│   ├── events/       # 活動管理功能
│   ├── feedback/     # 問卷與回饋系統
│   ├── member/       # 使用者註冊、登入、個人中心
│   ├── media/        # 上傳圖片與 QR Code 儲存
│   ├── static/       # 靜態資源
│   ├── templates/    # HTML 模板
│   └── project/      # Django 專案設定
├── zeabur.yaml       # Zeabur 部署設定
├── requirements.txt
└── README.md
```

## 🌍 Demo 網站（由 Zeabur 部署）

👉 [https://qbeep.zeabur.app/](https://qbeep.zeabur.app/)

---

🛡️ 若你想進一步協助我們優化、改進功能，歡迎提出 PR 或 Issue！
