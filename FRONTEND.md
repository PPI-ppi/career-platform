# Career Platform 前端架构

## 入口文件

| 文件 | 作用 |
|------|------|
| `src/main.js` | Vue 应用入口：挂载 Pinia 状态管理、Vue Router、Element Plus UI 库及全部图标 |
| `src/App.vue` | 全局布局：顶部导航栏（首页 / 能力目标库 / 实训与反馈 / 个人中心）+ 路由视图 `<router-view>` |

---

## 路由 (`src/router/index.js`)

| 路径 | 页面 | 说明 |
|------|------|------|
| `/` | Home.vue | 首页 |
| `/jobs` | JobExplorer.vue | **能力目标库** — 岗位列表、搜索、筛选 |
| `/job/:id` | JobDetail.vue | 岗位详情 + 知识图谱 |
| `/profile` | Index.vue | 个人中心布局（侧栏+子路由） |
| `/profile/info` | PersonalInfo.vue | 能力对标 — 七维雷达图 + AI 诊断 |
| `/profile/match` | JobMatch.vue | 人岗匹配结果 |
| `/profile/favorites` | FavoriteJobs.vue | 收藏岗位 |
| `/training` | GrowthTracker.vue | 个性化实训台 |
| `/feedback` | PolishAndExport.vue | 简历润色与导出 |

---

## API 层 (`src/api/`)

| 文件 | 封装的 API |
|------|-----------|
| `client.js` | **Axios 核心** — baseURL=`/api/v1`，自动获取 guest token，401 自动刷新，失败跳首页 |
| `auth.js` | 登录/注册/登出/刷新 token |
| `jobs.js` | 岗位列表、详情、搜索、热门 |
| `resume.js` | 简历上传、分析、获取画像 |
| `matching.js` | 人岗匹配、选定岗位、岗位图谱 |
| `careerPlan.js` | 职业规划 CRUD |
| `learningPlan.js` | 学习计划、每日任务、AI 教练 |
| `agents.js` | 智能体运行状态查询 |
| `diagnosis.js` | AI 深度诊断 |
| `favorites.js` | 收藏增删查 |
| `report.js` | 报告下载 (PDF/DOCX) |

---

## 页面 (`src/views/`)

### Home.vue — 首页
平台功能介绍、引导入口

### Jobs/ — 岗位模块
- **JobExplorer.vue** — 岗位列表页（能力目标库）
  - `loadJobs()` → 调 `/api/v1/jobs`
  - 响应映射：`job_title→title`，`company→company`，`salary_range→salary`
  - 无限滚动加载、关键词搜索（RAG）、行业/城市/薪资筛选
  - **关键：catch 静默失败 → `allJobs = []` → 空页面**
- **JobDetail.vue** — 岗位详情
  - 展示岗位基本信息 + 要求
  - 嵌入 `JobKnowledgeGraph` 组件（从 Neo4j `/api/v1/matching/job-graph` 拉取图谱数据）

### Profile/ — 个人中心
- **Index.vue** — 布局容器（左侧菜单 + 右侧子路由）
- **PersonalInfo.vue** — 上传简历 → 七维能力雷达图 → AI 诊断报告
- **JobMatch.vue** — 人岗匹配打分结果
- **FavoriteJobs.vue** — 收藏列表
- **AIReport.vue** — AI 生成报告预览
- **GrowthTracker.vue** — 个性化实训任务
- **PolishAndExport.vue** — 简历润色 + 导出 DOCX/PDF
- **profileState.js** — 个人中心共享状态（简历数据、画像数据、匹配结果）

---

## 组件 (`src/components/`)

| 文件 | 作用 |
|------|------|
| `RadarChart.vue` | 七维雷达图（专业技能/创新/学习/实习/抗压/沟通/证书） |
| `JobCard.vue` | 岗位卡片（JobExplorer 用） |
| `JobKnowledgeGraph.vue` | Neo4j 知识图谱可视化（节点+连线） |
| `PromotionGraph.vue` | 晋升路径图 |
| `InteractiveLoading.vue` | 带文案的加载动画 |

---

## 其他

| 路径 | 作用 |
|------|------|
| `src/stores/auth.js` | Pinia 状态：登录状态、用户信息 |
| `src/mock/promotionData.json` | 晋升路径静态数据 |
| `src/mock/promotion/*.json` | 各岗位晋升 mock 数据（10个岗位各一份） |
| `src/assets/*.png` | 插图、Logo |
| `src/assets/mockGraph.js` | 图谱 mock 数据 |

---

## 数据流（能力目标库为例）

```
JobExplorer.vue onMounted()
  → loadJobs()
  → jobsApi.list()  →  api.get('/jobs')
  → Axios client.js  →  GET /api/v1/jobs?page=1&page_size=200
  → Vite proxy  →  backend:8000/api/v1/jobs
  → FastAPI jobs.py  →  MySQL SELECT
  → 返回 {success:true, jobs:[...]}
  → mapped: job_title→title, salary_range→salary
  → allJobs = mapped
  → filteredJobs → displayedJobs → template v-for 渲染
```

---

## 关键问题点

**JobExplorer `loadJobs()` 第 258 行：**
```js
} catch {
    if (reset) allJobs.value = []
}
```
如果 API 请求失败（网络错误、500、CORS、token 刷新死循环），**静默失败，页面显示空状态**（"未找到相关职位"）。这是"能力目标库没有显示"的最可能根因。

**client.js 第 43-47 行：**
```js
localStorage.clear()
window.location.href = '/'
```
401 且 refresh token 也失败时，清空存储并跳首页。如果出现此行为，说明认证环节断了。
