# Skills Collection

蒐集 GitHub 上實用的 AI agent skills，以 git submodule 管理。

## 使用方式

```bash
# 初次 clone
git clone --recurse-submodules <repo-url>

# 更新所有 submodule 到最新
git submodule update --remote --merge
```

## Skills 列表

### 🛠 工程與開發

| Skill | 技能路徑 | 說明 |
|-------|----------|------|
| [agent-skills](https://github.com/addyosmani/agent-skills) | `agent-skills/skills` | Addy Osmani 的 24 個生產級工程技能，涵蓋完整開發生命週期（spec/plan/build/test/review/ship） |
| [mattpocock-skills](https://github.com/mattpocock/skills) | `mattpocock-skills/skills` | Matt Pocock 的「Skills For Real Engineers」— 可組合的小型技能（grill-me、TDD、domain modeling、code review、wayfinder） |
| [ponytail](https://github.com/DietrichGebert/ponytail) | `ponytail/skills` | 懶惰資深工程師技能 — 少寫 ~54% 程式碼，保留所有安全防護，使用 YAGNI 階梯（native > stdlib > dep > one line > minimum） |
| [superpowers](https://github.com/obra/superpowers) | `superpowers/skills` | Prime Radiant 的 AI Agent 完整開發方法論 — 包含 TDD、系統化排錯、腦力激盪、計畫撰寫與子 Agent 驅動開發等 14 個技能 |

### 🎨 設計與圖表

| Skill | 技能路徑 | 說明 |
|-------|----------|------|
| [architecture-diagram-generator](https://github.com/Cocoon-AI/architecture-diagram-generator) | `architecture-diagram-generator/architecture-diagram` | 將自然語言架構描述轉為暗色主題 HTML 圖表，支援 PNG/PDF 匯出 |
| [diagram-design](https://github.com/cathrynlavery/diagram-design) | `diagram-design/skills/diagram-design` | 編輯級品質圖表（27 種類型），讀取你的網站來適配品牌風格 |
| [huashu-design](https://github.com/alchaincyf/huashu-design) | `huashu-design` | 一句話出設計 — iOS 原型、HTML 簡報、動態圖形、資訊圖表、可編輯 PPTX |

### 🧠 思考與方法論

| Skill | 技能路徑 | 說明 |
|-------|----------|------|
| [fable-method](https://github.com/Sahir619/fable-method) | `fable-method/skills` | Think/act/prove 工作流，源自 Claude Fable 5，含對抗性評估與 fable-judge 驗證器 |
| [nuwa-skill](https://github.com/alchaincyf/nuwa-skill) | `nuwa-skill` | 將任何人的思維模型（Jobs、Musk、Munger、Feynman、Naval、PG 等）提煉為 agent 技能 |
| [prompt-engineering-expert](https://github.com/TomsTools11/prompt-engineering-expert) | `prompt-engineering-expert` | 完整的 prompt 工程技能：分析、生成、自訂指令、進階技巧、排錯與評估框架 |

### 🤖 Agent 最佳化

| Skill | 技能路徑 | 說明 |
|-------|----------|------|
| [caveman](https://github.com/JuliusBrussee/caveman) | `caveman/skills` | 讓 AI 用原始人方式說話 — 同樣的答案，減少 ~65% output tokens |
| [darwin-skill](https://github.com/alchaincyf/darwin-skill) | `darwin-skill` | 自主實驗迴圈最佳化 agent 技能，含 9 維評分、棘輪機制與 human-in-the-loop |
| [nopua](https://github.com/wuji-labs/nopua) | `nopua` | 反 PUA 技能 — 以信任取代恐懼驅動，benchmark 顯示比無技能多找 +104% 隱藏 bug |
| [pua](https://github.com/tanweai/pua) | `pua/skills` | 用企業 PUA/PIP 話術（14 種風格：阿里、字節、Netflix、Musk、Jobs 等）逼迫 AI 窮盡所有方案 |

### 📚 知識管理

| Skill | 技能路徑 | 說明 |
|-------|----------|------|
| [book-to-skill](https://github.com/virgiliojr94/book-to-skill) | `book-to-skill` | 將技術書籍（PDF/EPUB/DOCX）轉為 on-demand agent 技能，節省 24–51× tokens |
| [llm-wiki-skill](https://github.com/sdyckjq-lab/llm-wiki-skill) | `llm-wiki-skill` | 將碎片資訊轉為互連知識庫，含互動式離線知識圖譜（基於 Karpathy 的 llm-wiki 方法論） |
| [obsidian-skills](https://github.com/kepano/obsidian-skills) | `obsidian-skills/skills` | kepano 的 Obsidian agent 技能：obsidian-markdown、obsidian-bases、json-canvas、obsidian-cli、defuddle |
| [qmd](https://github.com/tobi/qmd) | `qmd/skills` | 搜尋與檢索本地 Markdown 知識庫、筆記、文件與 Wiki（支援 BM25 關鍵字、向量語意與 HyDE 查詢） |

### 🌐 領域專用

| Skill | 技能路徑 | 說明 |
|-------|----------|------|
| [kubernetes-skill](https://github.com/LukasNiessen/kubernetes-skill) | `kubernetes-skill` | 生產級 Kubernetes 技能，以 failure-mode-first 工作流防止幻覺 |
| [speak-human-tw](https://github.com/Raymondhou0917/speak-human-tw) | `speak-human-tw` | 繁體中文（台灣）去 AI 味改寫器 — 偵測 35+ AI 寫作模式，修正中國用法，改寫成人類語氣 |

### 📦 合集

| Skill | 技能路徑 | 說明 |
|-------|----------|------|
| [clawic-skills](https://github.com/clawic/skills) | `clawic-skills/skills` | Clawic 的精選開源技能合集 — 分類整理的 SKILL.md 檔案庫 |
