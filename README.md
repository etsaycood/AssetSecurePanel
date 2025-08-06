# 主機狀態儀表板

這是一個基於 Python Flask 框架和 SQLite 資料庫建立的簡單網頁儀表板，用於監控企業主機的防毒更新狀態和日誌接收狀態。它透過整合多個資料來源，提供分級、用途和主機層級的視覺化概覽。

## 功能

- **多層級概覽**: 提供從「分級」到「主機用途」再到「單一主機」的三層級儀表板視圖。
- **狀態燈號**: 根據設定的天數閾值，以綠、黃、紅三種顏色直觀顯示主機群組或單一主機的更新狀態。
  - **綠色**: 所有主機（或單一主機）在指定天數內都已更新。
  - **黃色**: 至少 80% 的主機在指定天數內已更新。
  - **紅色**: 少於 80% 的主機在指定天數內已更新。
- **可配置閾值**: 用戶可以輸入天數來調整更新狀態的判斷閾值。
- **假資料生成**: 包含用於生成模擬主機、防毒和日誌資料的腳本，方便快速部署和測試。

### 儀表板截圖

**分級概覽**
![分級概覽](images/主機儀表板 - 分級概覽.png)

**主機清單**
![主機清單]([images/主機清單.png](https://github.com/etsaycood/AssetSecurePanel/blob/main/%E4%B8%BB%E6%A9%9F%E6%B8%85%E5%96%AE.png))

## 專案結構

```
. (專案根目錄)
├── app.py                  # Flask 網頁應用程式主程式
├── generate_data.py        # 生成企業主機假資料 (hosts.db)
├── generate_antivirus_data.py # 生成防毒主機假資料 (antivirus.db)
├── generate_logserver_data.py # 生成 LogServer 主機假資料 (logserver.db)
├── update_dashboard_db.py  # 整合資料庫，用於儀表板 (dashboard.db)
├── templates/
│   ├── index.html          # 儀表板首頁 (分級概覽)
│   ├── purpose_detail.html # 第二層頁面 (主機用途概覽)
│   └── host_list.html      # 第三層頁面 (主機清單)
└── static/
    └── style.css           # 網頁樣式表
```

## 設定與執行

### 前置條件

請確保您的系統已安裝 Python 3.6 或更高版本。

### 安裝依賴

在專案根目錄下，開啟終端機並執行以下命令安裝所需的 Python 套件：

```bash
pip install Flask Faker
```

### 生成資料庫

在運行儀表板之前，您需要生成模擬資料。請按照以下順序執行腳本：

1.  **生成企業主機資料 (hosts.db)**
    ```bash
    python generate_data.py
    ```

2.  **生成防毒主機資料 (antivirus.db)**
    ```bash
    python generate_antivirus_data.py
    ```

3.  **生成 LogServer 主機資料 (logserver.db)**
    ```bash
    python generate_logserver_data.py
    ```

4.  **更新儀表板資料庫 (dashboard.db)**
    ```bash
    python update_dashboard_db.py
    ```

這些腳本將在專案根目錄下建立 `hosts.db`, `antivirus.db`, `logserver.db` 和 `dashboard.db` 檔案。

### 運行網頁儀表板

在專案根目錄下，執行以下命令啟動 Flask 應用程式：

```bash
python app.py
```

應用程式啟動後，您將在終端機中看到類似以下的訊息：

```
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

在您的網頁瀏覽器中打開 `http://127.0.0.1:5000/` 即可訪問儀表板。

## 授權

本專案採用 MIT License 授權。詳情請參閱 `LICENSE` 檔案。
