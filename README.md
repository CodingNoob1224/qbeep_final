
# QBeep 活動管理系統

一個以 Django 開發的活動報名與簽到平台，支援報名管理、簽到退、問卷填寫、後台分析等功能，並整合 QR Code、表單系統與權限管理機制，適合校內活動、社團管理或研討會場域使用。

## 🌟 專案特色

- 📝 活動報名系統（含人數上限與時間限制）
- 📥 使用者註冊、登入、自動登入、個人資訊編輯
- 📅 管理者可新增/修改活動
- 📤 報名後自動產生 QR Code，支援掃碼簽到
- ✅ 支援活動出席紀錄、問卷填寫與回饋統計
- 📊 管理後台提供報名人數、回饋率、回覆內容視覺化分析
- 🛡️ 權限區分：管理員 / 使用者
- 📦 支援 Zeabur 雲端部署、自動產 QR Code（Base64）

## 📷 預覽畫面

| 登入畫面 | 活動列表 | 個人頁面 |
|----------|----------|----------|
| ![login](screenshots/login.png) | ![events](screenshots/events.png) | ![profile](screenshots/profile.png) |

## 🛠️ 技術架構

- Python 3.12
- Django 5.1.1
- SQLite / 可擴充至 MySQL
- Bootstrap 5
- QRCode 模組
- Zeabur 自動部署 + `zeabur.yaml`

## 📦 安裝與啟動方式

```bash
git clone https://github.com/CodingNoob1224/qbeep_final.git
cd qbeep_final/app

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows 用 venv\Scripts\activate

# 安裝依賴套件
pip install -r requirements.txt

# 遷移資料庫
python manage.py migrate

# 啟動本地伺服器
python manage.py runserver
```

## 🧪 測試帳號

| 角色 | 帳號 | 密碼 |
|------|------|------|
| 管理員 | admin | admin123 |
| 一般使用者 | test1 | test123 |

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

## 🙌 製作人

- 郭佩芸（@CodingNoob1224）｜[GitHub](https://github.com/CodingNoob1224)
- 淡江大學 資訊工程學系

---

🛡️ 若你想進一步協助我們優化、改進功能，歡迎提出 PR 或 Issue！
