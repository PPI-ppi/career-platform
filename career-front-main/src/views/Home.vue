<template>
  <div class="home">
    <div>
    <!-- 1. 顶部区域 -->
    <header class="home-header">
      <div class="header-content">
        <h1 class="main-title">
          {{ typedText }}<span class="cursor">|</span>
        </h1>
        
        <!-- 搜索框 -->
        <div class="search-box">
          <el-input
            v-model="searchKeyword"
            placeholder="输入目标岗位（如：Java工程师），查看能力拆解与差距"
            size="large"
            clearable
            @keydown.enter="handleSearch"
            class="search-input"
          />
            
          <el-button 
            type="primary" 
            size="large"
            @click="handleSearch"
            class="search-btn"
          >
            <el-icon><Search /></el-icon>
            搜索
          </el-button>         
         </div>

        <!-- 热门搜索提示 -->
        <div class="hot-search">
          <span class="label">热门搜索：</span>
          <el-tag
            v-for="tag in hotSearchTags"
            :key="tag"
            size="small"
            class="search-tag"
            @click="searchByTag(tag)"
          >
            {{ tag }}
          </el-tag>
        </div>
      </div>
    </header>

    <!-- 2. 核心三列布局 -->
    <main class="home-main">
      <!-- 左列：职业分类卡片 -->
      <section class="left-panel category-panel">
        <el-card class="panel-card">
          <template #header>
            <div class="card-header">
              <el-icon><Grid /></el-icon>
              <span>能力需求风向标</span>
            </div>
          </template>
<div class="category-list-container"> <div class="scrolling-wrapper">
    <div class="scroll-content" v-for="n in 2" :key="n">
      <div
        v-for="(category, idx) in categories"
        :key="idx + '-' + n"
        class="category-item"
        @click="selectCategory(idx)"
      >
        <el-popover
          placement="right"
          :width="280"
          trigger="hover"
          popper-class="ai-monitor-popover"
          :show-after="100"
        >
          <template #reference>
            <div class="category-item-inner">
              <el-icon class="category-icon">
                <component :is="category.icon" />
              </el-icon>
              <div class="category-text">
                <span class="category-name">{{ category.name }}</span>
                <el-tag v-if="category.tag" size="small" effect="plain" class="category-tag">
                  {{ category.tag }}
                </el-tag>
              </div>
              <el-icon class="category-arrow"><ArrowRight /></el-icon>
            </div>
          </template>

          <div class="popover-ai-content">
            <div class="pop-header">
              <el-icon class="ai-pulse"><MagicStick /></el-icon>
              <span>AI能力建模·达标预测</span>
            </div>

            <div class="prediction-main">
              <div class="predict-item">
                <div class="predict-label-row">
                  <span class="label">岗位匹配度</span>
                  <span class="value" :class="matchScoreClass(category)">
                    {{ getMatchScore(category) ?? '--' }}<small v-if="getMatchScore(category) != null" class="score-unit">分</small>
                  </span>
                </div>
                <el-progress
                  v-if="getMatchScore(category) != null"
                  :percentage="getMatchScore(category)"
                  :stroke-width="8"
                  :show-text="false"
                  :color="matchProgressColor(category)"
                />
                <p v-if="getMatchScore(category) != null" class="base-info">基于你的七维能力画像对标分析</p>
                <p v-else class="base-info base-info-empty">暂未对标该岗位，请前往「能力对标」完成分析</p>
              </div>

              <div class="salary-forecast-card">
                <div class="forecast-item">
                  <span class="f-label">技能市场稀缺度指数</span>
                  <el-tag size="mini" :type="scarcityType(category)" effect="dark">
                    {{ category.insight.scarcity || '高' }}
                  </el-tag>
                </div>
                <div class="scarcity-info">
                  <span class="s-label">核心短板：</span>
                  <el-tag size="mini" type="danger" effect="plain">
                    {{ category.insight.weakness || '核心技能' }}
                  </el-tag>
                </div>
              </div>
            </div>

            <el-divider border-style="dashed" style="margin: 12px 0" />

            <div class="mentor-suggestion">
              <span class="suggestion-label">🤖 AI 学习策略：</span>
              <p class="suggestion-text">
                {{ generateAgentDecision(category) }}
              </p>
            </div>
          </div>
        </el-popover>
      </div>
    </div>
  </div>
</div>
        </el-card>
      </section>

      <!-- 中列：双功能入口卡片 -->
      <section class="middle-panel">
        <!-- 卡片 A：探索岗位 -->
        <div class="feature-card explore-card" @click="goToJobs">
          <div class="card-bg" style="background-image: url('https://placehold.co/600x300/667eea/ffffff?text=Explore+Jobs');"></div>
          <div class="card-overlay"></div>
          <div class="card-content">
            <h2 class="card-title">浏览能力目标库</h2>
            <p class="card-desc">岗位拆解能力图谱，对标差距</p>
            <el-button type="primary" size="large" class="card-btn">
              <el-icon><Search /></el-icon>
              立即浏览
            </el-button>
          </div>
        </div>

        <!-- 卡片 B：开始测评 -->
        <div class="feature-card assessment-card" @click="goToProfile">
          <div class="card-bg" style="background-image: url('https://placehold.co/600x300/764ba2/ffffff?text=Assessment');"></div>
          <div class="card-overlay"></div>
          <div class="card-content">
            <h2 class="card-title">校准我的技能基线</h2>
            <p class="card-desc">完善项目与技能数据，校准基线</p>
            <el-button type="success" size="large" class="card-btn">
              <el-icon><Document /></el-icon>
              立即校准
            </el-button>
          </div>
        </div>
      </section>

      <!-- 右列：个人画像面板 -->
      <section class="right-panel">
        <el-card class="panel-card roadmap-focus-card">
          <!-- 顶部状态栏 -->
          <div class="rp-status-bar">
            <div class="pulse-dot"></div>
            <span>AI 学习导师 · 职场导航</span>
          </div>

          <!-- 加载态 -->
          <div v-if="profileLoading" class="rp-loading">
            <el-skeleton :rows="5" animated />
          </div>

          <!-- 空态：未填写个人信息 -->
          <div v-else-if="!hasProfile" class="rp-empty">
            <div class="rp-empty-illustration">
              <svg viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="60" cy="60" r="56" fill="#f0f5ff" stroke="#d6e4ff" stroke-width="2" stroke-dasharray="6 4"/>
                <path d="M60 30c-8 0-14 6-14 14s6 14 14 14 14-6 14-14-6-14-14-14z" fill="#bfcfff"/>
                <path d="M38 78c0-12 10-22 22-22s22 10 22 22" stroke="#97aaff" stroke-width="3" stroke-linecap="round" fill="none"/>
                <circle cx="88" cy="36" r="6" fill="#ffd6d6"/>
                <path d="M85 36h6M88 33v6" stroke="#ff9999" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="rp-empty-title">暂无个人画像</div>
            <div class="rp-empty-desc">前往个人中心填写简历信息，<br/>AI 学习导师将为你生成职场画像与每日任务</div>
            <el-button type="primary" round class="rp-empty-btn" @click="router.push('/profile/info')">
              <el-icon><User /></el-icon> 前往个人中心
            </el-button>
          </div>

          <!-- 有数据：画像概览 -->
          <div v-else class="rp-content">
            <!-- 画像概览 -->
            <div class="rp-page rp-page-front">
              <!-- 用户头像行 + 综合评分 -->
              <div class="rp-user-row">
                <el-avatar :size="36" :src="auth.user?.avatar || ''" />
                <div class="rp-user-info">
                  <div class="rp-user-name">
                    {{ auth.user?.name || auth.user?.username || '用户' }}
                    <el-tag size="small" type="success" effect="plain">就绪</el-tag>
                  </div>
                  <div class="rp-user-sub">{{ auth.user?.university || auth.user?.school || '' }} {{ auth.user?.major ? '· ' + auth.user.major : '' }}</div>
                </div>
                <div class="rp-score-badge">
                  <div class="rp-score-num">{{ overallScore }}</div>
                  <div class="rp-score-label">综合评定</div>
                </div>
              </div>

              <!-- 能力雷达图 -->
              <div class="rp-radar-chart">
                <div ref="radarChartEl" class="radar-chart"></div>
              </div>

              <!-- 能力缺口词云 -->
              <div class="rp-gap-cloud">
                <div class="rp-gap-title">能力缺口词云</div>
                <div class="cloud-body">
                  <span
                    v-for="gap in skillGaps"
                    :key="gap.name"
                    :class="['cloud-tag', gap.level]"
                    :style="{ fontSize: cloudFontSize(gap) }"
                    :title="gap.status"
                  >{{ gap.name }}</span>
                  <span v-if="skillGaps.length === 0" class="rp-tasks-empty">暂无缺口数据</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 底部入口 -->
          <el-button type="primary" class="rp-bottom-btn" round @click="$router.push('/training')">
            查看我的动态实训路线 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </el-card>
      </section>
    </main>

    <!-- 3. 底部区域：数据粒子放射引力场 -->
    <section class="particle-section">
      <div class="data-particle-field" ref="particleContainer">
        <canvas ref="bgCanvas" class="bg-canvas"></canvas>

        <svg class="connection-lines" id="connection-lines">
          <defs>
            <linearGradient id="line-gradient">
              <stop offset="0%" stop-color="#409EFF" />
              <stop offset="100%" stop-color="#b18aff" />
            </linearGradient>
          </defs>
          <circle class="orbit-ring" cx="50%" cy="50%" fill="none" r="240" stroke="rgba(177, 138, 255, 0.15)" stroke-dasharray="8 8" stroke-width="1"></circle>
          <circle class="orbit-ring" cx="50%" cy="50%" fill="none" r="150" stroke="rgba(0, 219, 230, 0.1)" stroke-width="2"></circle>
          <g ref="dynamicLines"></g>
        </svg>

        <div class="center-text-block center-node" ref="centerNode">
          <div class="small-title">AURORA ENGINE 2.0</div>
          <div class="big-data">基于 <span class="highlight">10,000+</span> 职业能力基准模型</div>
          <div class="ai-analysis">复杂网络分析</div>
        </div>

        <div class="post-sphere data-node sphere-1" :ref="setNodeRef"><span class="label">前端开发</span></div>
        <div class="post-sphere data-node sphere-2" :ref="setNodeRef"><span class="label">产品经理</span></div>
        <div class="post-sphere data-node sphere-3" :ref="setNodeRef"><span class="label">AI 算法</span></div>
        <div class="post-sphere data-node sphere-4" :ref="setNodeRef"><span class="label">网络安全</span></div>
        <div class="post-sphere data-node sphere-5" :ref="setNodeRef"><span class="label">后端开发</span></div>
        <div class="post-sphere data-node sphere-6" :ref="setNodeRef"><span class="label">数据分析</span></div>
        <div class="post-sphere data-node sphere-7" :ref="setNodeRef"><span class="label">UI/UX</span></div>
        <div class="post-sphere data-node sphere-8" :ref="setNodeRef"><span class="label">运维 SRE</span></div>
        <div class="post-sphere data-node sphere-10" :ref="setNodeRef"><span class="label">全栈开发</span></div>
        <div class="post-sphere data-node sphere-11" :ref="setNodeRef"><span class="label">移动端</span></div>
        <div class="post-sphere data-node sphere-12" :ref="setNodeRef"><span class="label">云计算</span></div>
        <div class="post-sphere data-node sphere-13" :ref="setNodeRef"><span class="label">架构师</span></div>
        <div class="post-sphere data-node sphere-14" :ref="setNodeRef"><span class="label">交互设计</span></div>
        <div class="post-sphere data-node sphere-15" :ref="setNodeRef"><span class="label">游戏开发</span></div>
        <div class="post-sphere data-node sphere-16" :ref="setNodeRef"><span class="label">物联网 IOT</span></div>
      </div>
    </section>

    <!-- 3. 底部区域：实训任务预览（横向展开画廊） -->
    <section class="task-gallery-section">
      <div class="gallery-header">
        <h2 class="section-title">实训任务预览</h2>
        <span class="gallery-sub">与个性化实训台同步 · 悬停展开任务卡片</span>
      </div>

      <div class="accordion-gallery" ref="accordionRef" @mouseleave="onAccordionLeave">
        <div
          v-for="(task, idx) in coverflowTasks"
          :key="task.id"
          class="accordion-card"
          :class="{ active: activeAccordionIdx === idx }"
          :ref="(el) => { if (el) accordionCardRefs[idx] = el }"
          @mouseenter="onAccordionHover(idx)"
          @click="onAccordionCardClick(task, idx)"
        >
          <div class="accordion-card__inner">
            <div class="accordion-card__bg" :style="{ background: accordionGradients[idx % accordionGradients.length] }">
              <div v-if="task.status" class="accordion-card__progress" :class="statusClass(task.status)">
                <span class="progress-dot"></span>{{ task.status }}
              </div>
              <img class="accordion-card__thumb" :src="taskThumb" alt="" draggable="false" />
              <div class="accordion-card__overlay"></div>
              <div class="accordion-card__content">
                <div class="accordion-card__badge">T{{ idx + 1 }}</div>
                <div class="accordion-card__title">{{ task.title }}</div>
                <div v-if="task.description" class="accordion-card__desc">{{ task.description }}</div>
                <div class="accordion-card__steps">
                  <div
                    v-for="(step, si) in (task.steps || defaultSteps)"
                    :key="si"
                    class="accordion-card__step"
                  >
                    <span class="step-dot"></span>
                    <span>{{ step }}</span>
                  </div>
                </div>
                <div v-if="task.aiComment" class="accordion-card__comment">
                  <span class="comment-label">AI 简评</span>{{ task.aiComment }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 底部信息 -->
    <footer class="home-footer">
      <p>© 2026 职途无限 - AI 学习导师</p>
      <p class="footer-links">
        <el-link type="info">公司简介</el-link>
        <span class="divider">|</span>
        <el-link type="info">联系方式</el-link>
        <span class="divider">|</span>
        <el-link type="info">隐私政策</el-link>
        <span class="divider">|</span>
        <el-link type="info">服务条款</el-link>
      </p>
    </footer>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import {
  Search,
  User,
  Document,
  Grid,
  ArrowRight
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import gsap from 'gsap'
import taskThumb from '@/assets/retouch_2026080621010945.png'
import { resumeApi } from '@/api/resume'
import { learningPlanApi } from '@/api/learningPlan'
import { matchingApi } from '@/api/matching'
import { currentRadarData, dimensionDetailsRaw } from '@/views/Profile/profileState'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const RADAR_DIMS = ['专业技能', '创新能力', '学习能力', '实习能力', '抗压能力', '沟通能力', '证书']
const RADAR_WEIGHTS = [0.18, 0.15, 0.18, 0.16, 0.10, 0.10, 0.13]

const overallScore = computed(() => {
  const radar = currentRadarData.value
  if (!radar || !radar.some(v => v > 0)) return 0
  let totalScore = 0, totalWeight = 0
  radar.forEach((score, i) => {
    if (score > 0) {
      totalScore += score * RADAR_WEIGHTS[i]
      totalWeight += RADAR_WEIGHTS[i]
    }
  })
  return totalWeight > 0 ? Math.round(totalScore / totalWeight) : 0
})

const hasProfile = ref(false)
const profileLoading = ref(true)

const checkProfileStatus = async () => {
  try {
    // 1. 当前会话已填写（SPA 内 radar 数据非零）
    const hasRadar = currentRadarData.value && currentRadarData.value.some(v => v > 0)
    if (hasRadar) {
      hasProfile.value = true
      return
    }
    // 2. 从个人中心保存后跳转过来（一次性标记，读后即删）
    if (sessionStorage.getItem('profile_saved') === 'true') {
      sessionStorage.removeItem('profile_saved')
      hasProfile.value = true
      return
    }
    // 3. 未填写 → 显示空态
    hasProfile.value = false
  } catch {
    hasProfile.value = false
  } finally {
    profileLoading.value = false
  }
}

// ========== 能力雷达图 ==========
const radarChartEl = ref(null)
let radarChartInstance = null

const renderRadarChart = () => {
  if (!radarChartEl.value) return
  if (!radarChartInstance) {
    radarChartInstance = echarts.init(radarChartEl.value)
  }
  radarChartInstance.setOption({
    radar: {
      indicator: RADAR_DIMS.map((dim) => ({ name: dim, max: 100 })),
      radius: '68%',
      center: ['50%', '52%'],
      splitNumber: 4,
      axisName: { color: '#606266', fontSize: 10 },
      axisLine: { lineStyle: { color: '#e5e9f2' } },
      splitLine: { lineStyle: { color: '#e5e9f2' } },
      splitArea: { areaStyle: { color: ['rgba(64, 158, 255, 0.03)', 'rgba(64, 158, 255, 0.08)'] } },
    },
    series: [{
      type: 'radar',
      symbolSize: 4,
      data: [{
        value: RADAR_DIMS.map((_, i) => currentRadarData.value[i] || 0),
        name: '能力基线',
        areaStyle: { color: 'rgba(64, 158, 255, 0.25)' },
        lineStyle: { color: '#409EFF', width: 2 },
        itemStyle: { color: '#409EFF' },
      }],
    }],
  })
}

const disposeRadarChart = () => {
  if (radarChartInstance) {
    radarChartInstance.dispose()
    radarChartInstance = null
  }
}

// 词云字号：缺口越大（掌握度越低）字体越大
const cloudFontSize = (gap) => {
  const severity = 100 - (gap.percent || 70)
  const size = Math.max(12, Math.min(26, 13 + Math.round(severity / 7)))
  return `${size}px`
}

watch([hasProfile, currentRadarData], () => {
  if (hasProfile.value) {
    nextTick(() => renderRadarChart())
  }
}, { deep: true })

// 稀缺度指数对应的标签颜色：高=红 中=橙 低=绿
const scarcityType = (category) => {
  const s = category.insight?.scarcity
  if (s === '高') return 'danger'
  if (s === '中') return 'warning'
  return 'success'
};

// 学习策略：返回该岗位的定向学习建议
const generateAgentDecision = (category) =>
  category.insight?.decision || '建议优先补齐该岗位的核心技能缺口，再对标投递。';

const jobMatchResults = ref([])

// 从「能力对标」缓存或 API 获取岗位匹配结果（与 JobMatch 页共用同一数据源）
const loadJobMatchResults = async () => {
  try {
    // 1. 优先读 JobMatch 页写入的缓存
    const raw = sessionStorage.getItem('job_match_cache')
    if (raw) {
      const cached = JSON.parse(raw)
      if (cached.results?.length) {
        jobMatchResults.value = cached.results
        return
      }
    }
    // 2. 无缓存 → 直接调用对标接口（结果会同时写入 JobMatch 缓存）
    if (currentRadarData.value && currentRadarData.value.some(v => v > 0)) {
      const { data } = await matchingApi.match({
        radar_data: currentRadarData.value,
        dimension_details: dimensionDetailsRaw.value || undefined,
      })
      const payload = data.data || data
      const results = payload.ranked_results || payload.match_results || payload.matches || []
      if (results.length) jobMatchResults.value = results
    }
  } catch {
    // 对标数据不可用则保持空，popover 显示未对标提示
  }
}

// 按岗位名在匹配结果中查找分数（与 JobMatch 的 total_score 一致）
const getMatchScore = (category) => {
  const name = category?.name || ''
  const match = jobMatchResults.value.find((j) =>
    j.job_title && name && (j.job_title === name || j.job_title.includes(name) || name.includes(j.job_title)))
  return match && typeof match.total_score === 'number' ? match.total_score : null
}

const matchScoreClass = (category) => {
  const s = getMatchScore(category)
  if (s == null) return ''
  if (s >= 85) return 'score-excellent'
  if (s >= 70) return 'score-good'
  return 'score-warning'
}

const matchProgressColor = (category) => {
  const s = getMatchScore(category)
  if (s == null) return '#c0c4cc'
  if (s >= 85) return '#67c23a'
  if (s >= 70) return '#409eff'
  return '#e6a23c'
}

// 从 resume_analyzer 获取数据
const fetchDashboardData = async () => {
  try {
    const resumeRes = await resumeApi.analyze({})
    const rData = resumeRes.data
    // 能力缺口
    if (rData.skill_analysis) {
      const s = rData.skill_analysis
      const gaps = []
      Object.entries(s).forEach(([key, val]) => {
        const score = typeof val === 'number' ? val : 75
        if (score < 80) {
          gaps.push({
            name: key,
            status: score < 50 ? '缺失' : score < 70 ? '尚浅' : '待加强',
            level: score < 50 ? 'danger' : score < 70 ? 'warning' : 'info',
            percent: score,
            color: score < 50 ? '#f56c6c' : score < 70 ? '#e6a23c' : '#409eff',
          })
        }
      })
      if (gaps.length > 0) skillGaps.value = gaps.slice(0, 4)
    }

  } catch {
    // 静默降级，使用默认值
  }
}

onMounted(() => {
  fetchCoverflowTasks()
})

onUnmounted(() => {
  if (accordionTween) accordionTween.kill()
})



onMounted(() => {
  startTyping();
})

const router = useRouter()


const fullText = "职途虽远，智能无界；跨越方寸，预见无限"
const typedText = ref("")

// 修改你的 startTyping 函数
let typingTimer = null; // 在函数外部定义变量

const startTyping = () => {
  // 🌟 新增：如果已经在打字了，先停止之前的，防止重复
  if (typingTimer) clearInterval(typingTimer);
  typedText.value = ''; 
  
  let i = 0;
  typingTimer = setInterval(() => {
    typedText.value += fullText[i];
    i++;
    if (i >= fullText.length) {
      clearInterval(typingTimer);
      typingTimer = null;
    }
  }, 100);
};

// ========== 实训任务预览 · 横向展开画廊（GSAP 驱动）==========
const defaultSteps = ['搭建环境', '编写脚本', '压测验证']
const coverflowTasks = ref([])
const coverflowLoading = ref(false)

const accordionRef = ref(null)
const accordionCardRefs = ref([])
const activeAccordionIdx = ref(0) // 默认选中第一张

// 卡片背景渐变（半透明淡色系，配合毛玻璃）
const accordionGradients = [
  'linear-gradient(135deg, rgba(102, 126, 234, 0.30) 0%, rgba(118, 75, 162, 0.16) 100%)',
  'linear-gradient(135deg, rgba(240, 147, 251, 0.30) 0%, rgba(245, 87, 108, 0.16) 100%)',
  'linear-gradient(135deg, rgba(79, 172, 254, 0.30) 0%, rgba(0, 242, 254, 0.16) 100%)',
  'linear-gradient(135deg, rgba(67, 233, 123, 0.30) 0%, rgba(56, 249, 215, 0.16) 100%)',
  'linear-gradient(135deg, rgba(250, 112, 154, 0.30) 0%, rgba(254, 225, 64, 0.16) 100%)',
  'linear-gradient(135deg, rgba(161, 140, 209, 0.30) 0%, rgba(251, 194, 235, 0.16) 100%)',
  'linear-gradient(135deg, rgba(252, 203, 144, 0.30) 0%, rgba(213, 126, 235, 0.16) 100%)',
  'linear-gradient(135deg, rgba(224, 195, 252, 0.30) 0%, rgba(142, 197, 252, 0.16) 100%)',
  'linear-gradient(135deg, rgba(245, 87, 108, 0.30) 0%, rgba(255, 154, 158, 0.16) 100%)',
  'linear-gradient(135deg, rgba(102, 126, 234, 0.30) 0%, rgba(67, 233, 123, 0.16) 100%)',
]

const ACCORDION_GAP = 10
const EXPAND_RATIO = 0.52 // 展开卡片占整行比例

// 单张卡片展开/收起的 GSAP 动画
let accordionTween = null

const animateAccordion = (activeIdx) => {
  const cards = accordionCardRefs.value
  const container = accordionRef.value
  if (!cards.length || !container) return

  const n = cards.length
  const containerWidth = container.clientWidth
  const gaps = (n - 1) * ACCORDION_GAP
  const expandedWidth = containerWidth * EXPAND_RATIO
  const contractedWidth = (containerWidth - expandedWidth - gaps) / Math.max(n - 1, 1)

  if (accordionTween) accordionTween.kill()
  accordionTween = gsap.timeline()

  cards.forEach((card, i) => {
    if (!card) return
    const isActive = i === activeIdx

    accordionTween.to(card, {
      width: isActive ? expandedWidth : contractedWidth,
      rotationY: isActive ? 0 : (i < activeIdx ? -8 : 8),
      duration: 0.6,
      ease: 'power3.out',
      overwrite: 'auto',
    }, 0)

    const bg = card.querySelector('.accordion-card__bg')
    const overlay = card.querySelector('.accordion-card__overlay')
    const content = card.querySelector('.accordion-card__content')
    if (bg) {
      // 毛玻璃通透度 + 灰滤镜：激活卡片清晰彩色，未激活半透明 + 灰度
      gsap.to(bg, {
        opacity: isActive ? 1 : 0.55,
        filter: isActive ? 'grayscale(0%)' : 'grayscale(100%)',
        duration: 0.6,
        ease: 'power3.out',
        overwrite: 'auto',
      })
    }
    if (overlay) {
      gsap.to(overlay, {
        opacity: isActive ? 0 : 0.12,
        duration: 0.6,
        ease: 'power3.out',
        overwrite: 'auto',
      })
    }
    if (content) {
      // 视差漂移：非激活卡片内容微微平移，激活后归位
      const parallaxX = isActive ? 0 : (i < activeIdx ? -8 : 8)
      gsap.to(content, {
        opacity: isActive ? 1 : 0.7,
        x: parallaxX,
        duration: 0.5,
        ease: 'power3.out',
        overwrite: 'auto',
      })
    }
  })
}

const onAccordionHover = (idx) => {
  activeAccordionIdx.value = idx
  animateAccordion(idx)
}

// 鼠标离开画廊 → 恢复默认状态：第一张卡片展开
const onAccordionLeave = () => {
  activeAccordionIdx.value = 0
  animateAccordion(0)
}

// ----- 点击卡片 → 跳转个性化实训台 -----
const onAccordionCardClick = (task, idx) => {
  if (idx !== activeAccordionIdx.value) {
    onAccordionHover(idx)
    return
  }
  router.push({ path: '/training', query: { taskId: task.id } })
}

// 状态标签辅助函数
const statusClass = (s) => {
  if (s === '已完成') return 'status-done'
  if (s === '进行中') return 'status-doing'
  return 'status-todo'
}

// 后端任务状态 → 中文标签（与个性化实训台保持一致）
const normalizeStatus = (s) => {
  if (s === 'completed' || s === '已完成') return '已完成'
  if (s === 'in_progress' || s === '进行中') return '进行中'
  return '未开始'
}

// ----- 获取数据 -----
const fetchCoverflowTasks = async () => {
  coverflowLoading.value = true
  let list = []
  try {
    // 与个性化实训台共用同一数据源（learning-plan/tasks）
    const { data } = await learningPlanApi.getTasks()
    const raw = Array.isArray(data) ? data : (data?.tasks || [])
    list = raw.map((t) => ({
      id: t.id,
      title: t.title || t.task || t.content || '',
      description: t.description || '',
      status: normalizeStatus(t.status),
    }))
  } catch {
    // API 不可用
  }
  if (list.length === 0) {
    list = [
      { id: 1, title: '前端性能优化实战', description: '使用 Lighthouse 对首页做全量性能体检，针对首屏加载慢、JS 包体过大等问题逐项优化，将核心指标提升至 90 分以上并沉淀优化文档。', status: '进行中', steps: ['性能体检与基线', '代码分割与懒加载', '图片压缩与缓存策略', 'LCP 专项优化', '复测验证与归档'], aiComment: '首屏指标提升显著，FCP 已降至 2s 以内。下一步建议压缩 vendor 包体积并开启 preload，冲刺 LCP 90 分。' },
      { id: 2, title: '后端接口并发压测', description: '基于 JMeter 对核心下单链路设计阶梯加压场景，在 1000 QPS 目标下定位连接池耗尽与慢 SQL 瓶颈，通过参数调优与缓存改造完成性能验证。', status: '未开始', steps: ['压测场景与用例设计', '压测环境与脚本搭建', '阶梯加压与数据采集', '瓶颈定位与参数调优', '回归复测并输出报告'], aiComment: '该任务尚未启动。建议先梳理接口依赖与压测基线，并预留两个工作日用于瓶颈定位，避免影响后续排期。' },
      { id: 3, title: '全链路追踪实践', description: '在微服务中接入 OpenTelemetry SDK，通过 Jaeger 实现请求级链路追踪，配置合理的采样策略并接入告警，覆盖核心链路的调用拓扑可视化。', status: '已完成', steps: ['SDK 接入与埋点', '链路数据上报与展示', '采样策略与降噪配置', '链路告警与拓扑分析', '复盘并输出接入文档'], aiComment: '链路数据完整、采样率配置合理，告警覆盖核心链路。可接入日志关联与错误追踪，进一步提升排障效率。' },
      { id: 4, title: '自动化测试覆盖', description: '基于 Playwright 为核心业务模块编写 UI 自动化用例，覆盖登录、下单、支付等关键路径，集成到 CI 流水线实现每日回归并生成可视化报告。', status: '进行中', steps: ['测试框架与基线搭建', '核心用例编写', '异常分支与数据准备', 'CI 集成与定时回归', '报告与覆盖率分析'], aiComment: '关键路径用例已就绪，回归稳定通过。建议补齐异常分支与边界场景，将覆盖率目标提升至 70% 以上。' },
      { id: 5, title: '容器化部署实战', description: '编写多阶段 Dockerfile 构建轻量化镜像，使用 docker-compose 编排依赖服务，最终将应用一键部署到 K8s 集群并配置健康检查与自动扩缩容。', status: '未开始', steps: ['Dockerfile 编写与镜像瘦身', 'docker-compose 本地编排', '镜像仓库与 CI 推送', 'K8s 部署与探针配置', 'HPA 扩缩容与上线验证'], aiComment: '建议优先从基础镜像选型与多阶段构建入手控制镜像体积，部署阶段重点关注存活与就绪探针配置以及优雅停机。' },
      { id: 6, title: '数据库索引优化', description: '从慢查询日志中提取 Top SQL 逐条分析执行计划，针对高频查询条件设计复合索引，并通过覆盖索引策略验证读写性能的平衡。', status: '进行中', steps: ['慢查询日志采集', '执行计划分析', '复合索引设计', '索引效果验证', '冗余索引清理与归档'], aiComment: '复合索引收益明显，典型查询耗时下降 80% 以上。建议关注索引基数与写入放大，及时清理低效冗余索引。' },
    ]
  }
  coverflowTasks.value = list.map((t, i) => ({
    id: t.id ?? i + 1,
    title: t.title || t.name || t.text || `实训任务 ${i + 1}`,
    text: t.title || t.name || t.text || `实训任务 ${i + 1}`,
    description: t.description || '',
    status: t.status || '',
    aiComment: t.aiComment || '',
    steps: t.steps || t.step_breakdown || t.breakdown || defaultSteps,
  }))
  coverflowLoading.value = false
  nextTick(() => {
    // 默认激活第一张卡片
    activeAccordionIdx.value = 0
    animateAccordion(0)
  })
}

// 搜索相关
const searchKeyword = ref('')
const hotSearchTags = ref(['Java 工程师', '前端开发', '算法专家', '产品经理', '数据分析师', 'AI 工程师'])

// 职业分类
const categories = ref([
  { name: 'Java开发工程师', icon: 'Cpu', tag: '高需求', insight: { scarcity: '高', weakness: 'JVM 内存模型与并发编程', decision: '建议优先攻克 JVM 内存模型与并发编程，该技能在 Java 岗位中权重占比约 25%，且面试高频考察。' } },
  { name: 'C/C++开发工程师', icon: 'Cpu', tag: '硬核岗', insight: { scarcity: '高', weakness: '内存管理与多线程性能优化', decision: '建议优先攻克内存管理与多线程优化，C/C++ 岗位中底层性能优化能力权重占比约 30%，是区分度最高的技能。' } },
  { name: '前端开发工程师', icon: 'Monitor', tag: '热门岗', insight: { scarcity: '中', weakness: '框架源码与性能优化', decision: '建议优先攻克前端框架源码分析与性能优化，该技能在面试中权重占比约 22%，直接影响项目架构能力评估。' } },
  { name: '软件测试工程师', icon: 'CircleCheck', tag: '品质岗', insight: { scarcity: '中', weakness: '自动化测试框架设计', decision: '建议优先攻克自动化测试框架设计，该技能在测试岗位中权重占比约 25%，是中高级测试岗位的核心要求。' } },
  { name: '软件测试工程师(专项方向)', icon: 'CircleCheck', tag: '专项岗', insight: { scarcity: '中', weakness: '性能测试与安全测试', decision: '建议优先攻克性能测试与安全测试，专项测试能力在高级岗位中权重占比约 28%，是薪资提升的关键。' } },
  { name: '硬件测试工程师', icon: 'Setting', tag: '技术岗', insight: { scarcity: '高', weakness: '硬件信号测试与可靠性分析', decision: '建议优先攻克硬件信号测试与可靠性分析，该技能在硬件测试岗位中权重占比约 25%，是岗位核心能力。' } },
  { name: '实施工程师', icon: 'Setting', tag: '项目型', insight: { scarcity: '中', weakness: '系统部署与多方协调', decision: '建议优先攻克系统部署方案设计与项目实施协调，该技能在实施岗位中权重占比约 20%，是项目交付的关键。' } },
  { name: '技术支持工程师', icon: 'User', tag: '服务型', insight: { scarcity: '低', weakness: '复杂问题排查与故障分析', decision: '建议优先攻克复杂问题排查与故障分析，该技能在技术支持岗位中权重占比约 22%，直接影响客户满意度。' } },
  { name: '游戏运营', icon: 'MagicStick', tag: '运营岗', insight: { scarcity: '低', weakness: '数据分析与用户增长策略', decision: '建议优先攻克数据分析与用户增长策略，该技能在游戏运营岗位中权重占比约 25%，是精细化运营的基础。' } },
  { name: '科研人员', icon: 'Document', tag: '研究型', insight: { scarcity: '高', weakness: '论文复现与创新方法设计', decision: '建议优先攻克论文复现与创新方法设计，该技能在科研岗位中权重占比约 30%，是产出高质量成果的前提。' } }
]);

// 搜索处理
const handleSearch = () => {
  if (!searchKeyword.value.trim()) {
    ElMessage.info({
    message: '请输入搜索关键词',
    duration: 1500 // 设置为 1.5 秒 (1500ms)，你可以改成 1000, 800 等更短的时间
})
    return
  }
  router.push(`/jobs?keyword=${encodeURIComponent(searchKeyword.value)}`)
}

// 标签搜索
const searchByTag = (tag) => {
  searchKeyword.value = tag
  handleSearch()
}

// 选择分类
const selectCategory = (idx) => {
  const category = categories.value[idx]
  console.log('选择分类:', category?.name)
  // 预留跳转或筛选逻辑
  router.push(`/jobs?category=${idx + 1}`)
}

// 路由跳转
const goToJobs = () => router.push('/jobs')
const goToProfile = () => router.push('/profile/info')

// ========== 数据粒子放射引力场 ==========
const particleContainer = ref(null)
const bgCanvas = ref(null)
const centerNode = ref(null)
const dynamicLines = ref(null)
const dataNodes = ref([])

const setNodeRef = (el) => {
  if (el && !dataNodes.value.includes(el)) {
    dataNodes.value.push(el)
  }
}

let animationFrameId;
let canvasCtx;
let particles = [];
let mouse = { x: -1000, y: -1000 }; // 初始隐藏鼠标

// 1. 初始化 Canvas 粒子
const initCanvas = () => {
  if (!bgCanvas.value || !particleContainer.value) return;
  const rect = particleContainer.value.getBoundingClientRect();
  bgCanvas.value.width = rect.width;
  bgCanvas.value.height = rect.height;
  canvasCtx = bgCanvas.value.getContext('2d');

  particles = [];
  for (let i = 0; i < 500; i++) {
    particles.push({
      x: Math.random() * rect.width,
      y: Math.random() * rect.height,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5,
      size: Math.random() * 2 + 1,
      color: Math.random() > 0.5 ? 'rgba(64, 158, 255, 0.3)' : 'rgba(177, 138, 255, 0.3)'
    });
  }
}

// 2. 主渲染循环 (Canvas 粒子 + SVG 连线)
const renderLoop = () => {
  if (!canvasCtx || !bgCanvas.value || !particleContainer.value) return;
  const rect = particleContainer.value.getBoundingClientRect();

  // 清空画布
  canvasCtx.clearRect(0, 0, rect.width, rect.height);

  // 渲染粒子
  particles.forEach(p => {
    p.x += p.vx;
    p.y += p.vy;
    if (p.x < 0 || p.x > rect.width) p.vx *= -1;
    if (p.y < 0 || p.y > rect.height) p.vy *= -1;

    // 🌟 鼠标排斥效果 (Stitch 特效)
    let dx = mouse.x - p.x;
    let dy = mouse.y - p.y;
    let dist = Math.sqrt(dx * dx + dy * dy);
    if (dist < 150) {
      p.x -= dx * 0.01;
      p.y -= dy * 0.01;
    }

    canvasCtx.fillStyle = p.color;
    canvasCtx.beginPath();
    canvasCtx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
    canvasCtx.fill();
  });

  // 🌟 实时更新 SVG 动态连线 (从中心到每个球)
  if (centerNode.value && dynamicLines.value && dataNodes.value.length > 0) {
    const cRect = centerNode.value.getBoundingClientRect();
    const cx = cRect.left + cRect.width / 2 - rect.left;
    const cy = cRect.top + cRect.height / 2 - rect.top;

    // 获取之前生成的 path，如果没有则创建
    let paths = dynamicLines.value.querySelectorAll('path');
    if (paths.length === 0) {
      dataNodes.value.forEach(() => {
        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        path.setAttribute("stroke", "url(#line-gradient)");
        path.setAttribute("fill", "none");
        path.setAttribute("stroke-width", "1.5");
        path.setAttribute("opacity", "0.25");
        path.setAttribute("stroke-dasharray", "5, 5");
        dynamicLines.value.appendChild(path);
      });
      paths = dynamicLines.value.querySelectorAll('path');
    }

    dataNodes.value.forEach((node, i) => {
      const nRect = node.getBoundingClientRect();
      const nx = nRect.left + nRect.width / 2 - rect.left;
      const ny = nRect.top + nRect.height / 2 - rect.top;
      // 绘制贝塞尔曲线增加科技感
      paths[i].setAttribute("d", `M ${cx} ${cy} Q ${cx} ${ny} ${nx} ${ny}`);
    });
  }

  animationFrameId = requestAnimationFrame(renderLoop);
}

// 3. 鼠标交互事件
const handleMouseMove = (e) => {
  if (!particleContainer.value) return;
  const rect = particleContainer.value.getBoundingClientRect();
  mouse.x = e.clientX - rect.left;
  mouse.y = e.clientY - rect.top;

  // 🌟 磁性吸引效果 (GSAP)
  dataNodes.value.forEach(node => {
    const nRect = node.getBoundingClientRect();
    const centerX = nRect.left + nRect.width / 2;
    const centerY = nRect.top + nRect.height / 2;
    const dx = e.clientX - centerX;
    const dy = e.clientY - centerY;
    const distance = Math.sqrt(dx*dx + dy*dy);

    if (distance < 200) {
      gsap.to(node, {
        x: dx / 8, y: dy / 8, duration: 0.6, ease: 'power2.out', overwrite: 'auto'
      });
    } else {
      // 恢复原状
      gsap.to(node, { x: 0, y: 0, duration: 0.8, ease: 'elastic.out(1, 0.5)' });
    }
  });
}

// 4. GSAP 随机悬浮动画
const startGsapFloating = () => {
  dataNodes.value.forEach(node => {
    gsap.to(node, {
      y: `+=${(Math.random() - 0.5) * 30}`,
      x: `+=${(Math.random() - 0.5) * 20}`,
      duration: 3 + Math.random() * 2,
      ease: "sine.inOut",
      repeat: -1,
      yoyo: true
    });
  });
}

// ==========================================
// 🌟 升级版：个性化爆炸放射动画
// ==========================================
const runExplosionAnimation = () => {
  const tl = gsap.timeline();

  // 1. 中心文字块先显现 (稍微带一点点放大效果)
  if (centerNode.value) {
    tl.from(centerNode.value, {
      scale: 0.5,         // 从 0.5 倍大小开始
      opacity: 0,         // 从透明开始
      duration: 1.2,        // 持续 1.2 秒
      ease: "power4.out" // 带有弹性的出场缓动
    });
  }

  // 2. 🌟 核心：所有岗位球个性化、不同速放射
  if (dataNodes.value.length > 0) {
    // 技巧：我们遍历每个节点，为它们创建单独的 GSAP 动画
    dataNodes.value.forEach((node, index) => {

      // 🌟 生成随机参数，确保每个球都是独一无二的
      // 1. 速度随机：放射持续时间在 1.2秒 到 2.2秒 之间
      const randomDuration = 1.2 + Math.random() * 1.0;
      // 2. 延迟随机：每个球都在文字显现后 0 到 0.6秒 之间随机放射
      const randomDelay = Math.random() * 0.6;
      // 3. 缓动随机：大部分先快后慢，小部分稍微带一点弹性
      const randomEase = Math.random() > 0.8 ? "back.out(1.5)" : "power4.out";
      // 4. 景深随机：从不同的深远度发散出来
      const randomDepth = -300 - Math.random() * 300;

      gsap.from(node, {
        // 初始状态：全部压制到容器中心
        x: 0,
        y: 0,
        z: randomDepth,    // 🌟 关键：景深随机

        opacity: 0,         // 从透明开始
        scale: 0,           // 从 0 大小开始

        // 应用随机生成的参数
        duration: randomDuration, // 🌟 关键：速度随机
        delay: 0.2 + randomDelay,   // 🌟 关键：启动时差随机
        ease: randomEase,         // 🌟 关键：缓动随机

        // 在最后一个球（随机到的最慢的球）完成时，交棒给漂浮动画
        // 技巧：这里使用一个标志位，只让最后一个动画触发回调
        onComplete: () => {
          if (index === dataNodes.value.length - 1) {
            // 确保漂浮动画在放射完成后才开始
            startGsapFloating();
          }
        }
      });
    });
  }
};

// ==========================================
// 粒子引力场生命周期
// ==========================================
onMounted(() => {
  // 启动 Stitch 特效
  nextTick(() => {
    initCanvas();
    renderLoop();
    startGsapFloating();
    window.addEventListener('mousemove', handleMouseMove);

    const observerOptions = {
      root: null, // 默认使用浏览器视口
      threshold: 0.3 // 当 30% 的区域进入视口时触发
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        // 如果区域进入视口 且 动画尚未执行过
        if (entry.isIntersecting) {
          runExplosionAnimation(); // 执行放射动画
          observer.unobserve(entry.target); // 动画只跑一次，触发后停止观察
        }
      });
    }, observerOptions);

    if (particleContainer.value) {
      observer.observe(particleContainer.value);
    }
  });
})

// 生命周期
onMounted(() => {
  checkProfileStatus()
  fetchDashboardData()
  loadJobMatchResults()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('mousemove', handleMouseMove)
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
  disposeRadarChart()
})

const handleResize = () => {
  radarChartInstance?.resize()
}
</script>

<style scoped lang="scss">
.home {
  min-height: 100vh;
  background: #c4d1f617;
  
}

/* 找到 Home.vue 中的 .main-title 进行替换 */
.main-title {
  /* 🌟 大气点：巨大的字号配合极大的字间距 */
  font-size: 56px; 
  font-weight: 800;
  letter-spacing: 6px; /* 产生一种跨越感 */
  

  
  /* 选用更硬朗的字体 */
  font-family: "Inter", "PingFang SC", "Source Han Sans CN", "Microsoft YaHei", sans-serif;
  
  /* 增加一点文字阴影的深度感（非常淡） */
  text-shadow: 0 10px 20px rgba(0, 0, 0, 0.05);
  
  line-height: 1.3;
}

// ========== 1. 顶部区域 (修正了布局与层级) ==========
// ========== 1. 顶部区域 ==========
.home-header {
  background: linear-gradient(-45deg, #ff9a9e, #fad0c4, #afcaf4, #b1efbf);
  background-size: 400% 400%;
  animation: gradientBG 8s ease infinite; 
  padding: 5px 40px 100px; 
  color: #ffffff;
  position: relative;
  overflow: hidden;

 &::before { 
    content: "";
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background-image: radial-gradient(circle at 20% 30%, rgba(64, 158, 255, 0.15) 0%, transparent 50%);
    pointer-events: none;
    z-index: 1;
  }

  // 2. 🔥 新增：底部融合渐变层
  &::after {
    content: "";
    position: absolute;
    left: 0;
    bottom: 0;
    width: 100%;
    height: 150px; // 渐变过渡的高度，可以根据视觉效果调整
    /* 这里的 #f4f7fe 是根据你 .home 的 background: #bfcdf62e 计算出的近似底色 */
    background: linear-gradient(to bottom, transparent, #f4f7fe); 
    z-index: 2;
    pointer-events: none;
  }

  .header-content {
    max-width: 1200px;
    margin: 0 auto;
    position: relative;
    z-index: 3; // 确保文字内容在渐变层之上，不会变淡
  }

  .main-title {
    font-size: 52px;
    font-weight: 800;
    text-align: left;
    margin-bottom: 40px;
    min-height: 70px; 
    .cursor {
      margin-left: 8px;
      color: #409EFF;
      animation: blink 0.8s infinite;
    }
  }

  /* 🌟 搜索框样式块开始 */
/* ========================================================== */
/* 🔍 搜索组件深度美化：更精致、更协调、更有重点 */
/* ========================================================== */
.search-box {
  display: flex;
  align-items: stretch; /* 🌟 关键：确保按钮和输入框高度完美一致 */
  max-width: 1100px;      /* 🌟 稍微加宽，更显大气 */
  margin-bottom: 25px;
  position: relative;
  z-index: 10;

  /* -------------------------- */
  /* A. 左侧输入框：轻盈毛玻璃感 (虚) */
  /* -------------------------- */
  .search-input {
    flex: 1; /* 占满剩余空间 */

    :deep(.el-input__wrapper) {
      /* 1. 核心：轻量毛玻璃质感 (不破坏背景感) */
      background-color: rgba(255, 255, 255, 0.45) !important; 
      backdrop-filter: blur(12px); /* 🌟 核心：模糊后方背景 */
      
      /* 2. 圆角处理：左侧大圆角，右侧直角对接按钮 */
      border-radius: 24px 0 0 24px !important; 
      
      /* 3. 精致细节：极淡的描边与大阴影增加精致感 */
      border: 1px solid rgba(255, 255, 255, 0.4) !important;
      box-shadow: 0 8px 32px rgba(31, 38, 135, 0.05) !important;
      padding-left: 18px;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

      /* 控制输入框高度 (🌟 如果你用大字号，建议也增高) */
      .el-input__inner {
        height: 56px; 
        font-size: 16px;
        color: #334455;
        font-weight: 500;
        
        /* 占位符文字调淡 */
        &::placeholder {
          color: rgba(51, 68, 85, 0.4);
        }
      }
    }

    /* 4. 聚焦时的发光交互：更通透 */
    :deep(.el-input__wrapper.is-focus) {
      background-color: rgba(255, 255, 255, 0.9) !important; /* 聚焦时变清晰 */
      box-shadow: 0 8px 32px rgba(64, 158, 255, 0.15) !important;
      border-color: rgba(64, 158, 255, 0.5) !important;
    }
  }

  /* -------------------------- */
  /* B. 右侧按钮：坚实渐变色 (实 - 全场焦点) */
  /* -------------------------- */
  .search-btn {
    /* 1. 修改圆角：左侧直角对接输入框，右侧保留大圆角 */
    border-radius: 0 24px 24px 0 !important; 
    
    /* 2. 核心修改：坚实、饱和的渐变色 (钉在界面上) */
    background: linear-gradient(135deg, #77b1f8 0%, #8c97f6 100%) !important;
    color: white !important; /* 🌟 保证文字必须是纯白 */
    
    /* 3. 尺寸与字号优化 */
    padding: 0 45px !important; /* 增加点击区域和视觉分量 */
    font-weight: 700;           /* 🎨 加粗标题 */
    font-size: 18px;            /* 🎨 调大字号 */
    letter-spacing: 1px;        /* 字间距增加精致感 */
    height: auto;               /* 跟随容器高度，确保无缝 */
    border: none !important;
    
    /* 4. 重点：亮蓝色立体投影 (增加点击欲) */
    box-shadow: 4px 6px 15px rgba(64, 158, 255, 0.3) !important;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    cursor: pointer;

    /* 调整图标大小 */
    .el-icon {
      font-size: 20px;
      margin-right: 6px;
      vertical-align: middle;
    }

    /* 5. 悬停时的灵动交互 */
    &:hover {
      filter: brightness(1.1); /* 稍微变亮 */
      transform: translateY(-1px); /* 🎨 轻微上浮，产生交互反馈 */
      box-shadow: 4px 8px 25px rgba(64, 158, 255, 0.4) !important;
    }
    
    /* 按下时的反馈 */
    &:active {
      transform: translateY(1px); /* 轻微按下 */
      filter: brightness(1);
    }
  }
}

  .hot-search {
    display: flex;
    align-items: center;
    gap: 12px;
    .label { font-size: 14px; opacity: 0.8; }
    .search-tag {
      background: rgba(255, 255, 255, 0.1);
      color: #fff;
      cursor: pointer;
    }
  }
} // 闭合 .home-header
// ========== 2. 核心三列布局 (修正层级遮挡) ==========
.home-main {
  display: grid;
  grid-template-columns: 280px 1fr 320px;
  align-items: stretch;     /* 🌟 确保所有网格项（左中右）高度拉伸一致 */
  gap: 24px;
  max-width: 1400px;
  margin: -60px auto 10px; 
  padding: 0 40px;
  position: relative;
  z-index: 10; 

  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
    margin-top: 20px;
  }
}

// ========== 3. 通用卡片与面板样式 ==========
.panel-card {
  height: 100%;             /* 🌟 关键：让卡片填满整个网格区域的高度 */
  display: flex;            /* 开启 flex 布局以便内部内容分布 */
  flex-direction: column;   
  
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: none;

  // ... 其他代码 ...
  
  // 如果你想让里面的分类列表均匀撑开，可以给列表加这个：
  .category-list {
    flex: 1;                /* 🌟 让列表占据剩余的所有垂直空间 */
    display: flex;
    flex-direction: column;
    justify-content: space-around; /* 或者 space-between，取决于你想要的间距感 */
  }
}

/* 左列：职业分类 */
/* 左列：职业分类美化 */
/* ========================================================== */
/* 🎨 职业分类 (左列) 美化：毛玻璃质感与灵动交互 */
/* ========================================================== */
.category-panel {
  /* 1. 卡片主体材质美化 */
  .panel-card {
    border-radius: 20px !important;
    /* 🌟 修改点：透明度从 0.6 改为 0.92，增加实体感 */
    background: rgba(255, 255, 255, 0.72) !important; 
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.8); /* 边框也稍微白一点 */
    /* 🌟 修改点：阴影稍微加深，让它“压”住背景 */
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08) !important;
    height: 570px; /* 这个高度约等于原本容器的高度 */
    overflow: hidden; /* 确保溢出的卡片不可见，动画才能生效 */
    
    

    &:hover {
      box-shadow: 0 16px 50px rgba(64, 158, 255, 0.08); /* 悬停时阴影变深 */
    }

    /* 卡片头部标题美化 */
    :deep(.el-card__header) {
      padding: 22px 25px 15px; /* 增加内边距呼吸空间 */
      border-bottom: 1px solid rgba(0, 0, 0, 0.05); /* 调淡下划线 */

      .card-header {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 18px;          /* 🎨 调大标题：从 16px 改为 18px */
        font-weight: 700;         /* 🎨 加粗标题 */
        color: #334455;           /* 深灰蓝，非纯黑 */

        /* 标题图标美化 */
        i {
          font-size: 20px;
          color: #409EFF;         /* 使用 Header 强调色 */
        }
      }
    }
  }

/* 找到 .category-list-container 并替换为以下内容 */
/* 1. 找到并替换这部分代码 */
.category-list-container {
  /* 必须锁定一个比内容小的固定高度，overflow:hidden 才会生效 */
  height: 440px !important; 
  flex: none !important;    
  position: relative;
  padding: 10px 0;
  
  /* 核心：彻底切断用户的滚动交互（滚轮、触摸、拖拽） */
  overflow: hidden !important; 
  touch-action: none !important;   /* 禁用移动端/触摸板手势 */
  user-select: none;               /* 防止选取文字导致的拉拽滚动 */

  /* 2. 视觉：全浏览器兼容隐藏滚动条 */
  -ms-overflow-style: none !important;  /* IE/Edge */
  scrollbar-width: none !important;     /* Firefox */
  
  &::-webkit-scrollbar {
    display: none !important;           /* Chrome/Safari/Opera */
    width: 0 !important;
    height: 0 !important;
  }
}

/* 3. 动画执行层 */
.scrolling-wrapper {
  display: flex;
  flex-direction: column;
  /* 30秒滚完一圈，你可以根据体感调快（如20s）或调慢（如40s） */
  animation: scrollVertical 20s linear infinite;
}

/* 4. 关键交互：悬停时暂停滚动，方便用户查看 Popover */
.category-list-container:hover .scrolling-wrapper {
  animation-play-state: paused;
}

/* 5. 编写无缝滚动动画 */
@keyframes scrollVertical {
  0% {
    transform: translateY(0);
  }
  100% {
    /* 因为我们在 HTML 中 v-for="n in 2" 渲染了两组相同的数据 */
    /* 所以位移到 -50% 的位置时，视觉上正好回到起点，实现无缝连接 */
    transform: translateY(-50%);
  }
}

  /* 2. 职业分类列表通用美化 */
  .category-list {
    display: flex;
    flex-direction: column;
    gap: 6px;                     /* 🎨 调小间距：更紧凑、更有秩序感 */
    padding: 10px 12px 20px;     /* 🎨 底部留呼吸空间 */
  }

  /* 3. 职业分类单项交互美化 */
  .category-item {
    display: flex;
    align-items: center;
    padding: 8px 20px;          /* 🎨 增加点击区域和侧边空间 */
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); /* 🎨 高级缓动：更有弹性 */
    border: 1px solid transparent; /* 预留边框空间 */
    position: relative;
    overflow: hidden;

    

    .category-item-inner {
      display: flex;
      align-items: center;
      width: 100%;
    }

    /* A. 默认图标颜色微调 */
    .category-icon {
      font-size: 18px;
      margin-right: 14px;
      color: #90a4ae;              /* 🎨 默认态调淡图标：灰蓝色，减少干扰 */
      transition: all 0.3s ease;
      align-self: flex-start;
      margin-top: 2px;
    }
    .category-text {
      flex: 1;
      min-width: 0;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: 2px;
    }
    .category-name {
      font-size: 15px;
      font-weight: 500;            /* 中等粗细 */
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 100%;
      transition: all 0.3s ease;
    }
    .category-tag {
      margin: 0;
      padding: 1px 8px;
      font-size: 11px;
      line-height: 16px;
      border-radius: 4px;
      color: #409eff;
      background: rgba(64, 158, 255, 0.08);
      border-color: rgba(64, 158, 255, 0.2);
    }
    .category-arrow {
      font-size: 12px;
      color: #c0c4cc;
      opacity: 0.5;                /* 🎨 调淡箭头：静态下不明显 */
      transition: all 0.3s ease;
      margin-left: 6px;
      flex-shrink: 0;
    }

    /* B. 悬停态 (Hover)：灵动反馈 */
    &:hover {
      background: rgba(64, 158, 255, 0.08); /* 浅蓝色半透明背景 */
      color: #409EFF;              /* 文字和图标变蓝 */
      transform: translateX(6px);  /* 🎨 核心修改：整体分类项平滑向右移，更有灵性 */
      
      .category-icon { color: #409EFF; }
      .category-arrow { 
        transform: translateX(3px); /* 箭头多移一点点，增加视觉前推感 */
        opacity: 1;                /* 箭头变清晰 */
      }
    }

    /* C. 激活态 (Active)：呼吸渐变 */
    &.active {
      background: linear-gradient(135deg, #409EFF 0%, #0076FF 100%); /* 🎨 使用渐变色块：替换纯蓝色块，呼应全局配色 */
      color: #ffffff;
      box-shadow: 0 4px 15px rgba(64, 158, 255, 0.3); /* 🎨 激活项微弱外发光，增加呼吸感 */

      /* 激活态文字与图标全部白色 */
      .category-icon, .category-name, .category-arrow { color: #ffffff; opacity: 1; }
      
      /* 🎨 激活态取消位移反馈 */
      &:hover { transform: none; } 
    }
  }
}

.popover-ai-content {
  .ai-pulse {
    color: #409eff;
    animation: breath 2s infinite;
  }

  .prediction-main {
    .predict-item {
      margin-bottom: 15px;
      .predict-label-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        margin-bottom: 6px;
        .label { font-size: 13px; color: #606266; }
        .value { font-size: 20px; font-weight: bold; }
        .success-text { color: #67c23a; }
      }
      .base-info { font-size: 11px; color: #909399; margin-top: 5px; }
      .base-info-empty { font-style: italic; }
      .score-unit { font-size: 12px; color: #94a3b8; margin-left: 2px; font-weight: 600; }
      .score-excellent { color: #67c23a; }
      .score-good { color: #409eff; }
      .score-warning { color: #e6a23c; }
    }

    .salary-forecast-card {
      background: rgba(64, 158, 255, 0.06);
      border-radius: 8px;
      padding: 10px;
      .forecast-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
        .f-label { color: #606266; font-size: 12px; font-weight: bold; }
      }
      .scarcity-info {
        display: flex;
        align-items: center;
        font-size: 11px;
        color: #909399;
      }
    }
  }

  .mentor-suggestion {
    background: #f0f7ff;
    padding: 10px;
    border-radius: 6px;
    .suggestion-label { color: #409eff; font-weight: bold; font-size: 12px; }
    .suggestion-text { font-size: 12px; color: #606266; margin: 4px 0 0; }
  }
}

@keyframes breath {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.1); }
}

.middle-panel {
  display: flex;          /* 🌟 开启布局 */
  flex-direction: column; /* 纵向排列 */
  gap: 20px;              /* 🌟 这里的 gap 代替你之前的 margin-top */
  height: 100%;           /* 填满 Grid 容器高度 */
}

/* 卡片主体材质 */
.feature-card {
  position: relative;
  flex: 1;
  min-height: 200px;
  border-radius: 20px;       /* 🎨 调大圆角：增加柔和感，从 16px 改为 20px */
  overflow: hidden;
  cursor: pointer;
  transition: all 0.4s ease; /* 🎨 平滑过渡：增加时长 */
  
  background-color: rgba(255, 255, 255, 0.7) !important; 
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.9);
  /* 🌟 修改点：投影增强 */
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.06) !important;


  // 去掉背景图 (约第 348 行)
  .card-bg {
    display: none; 
  }

  // 修改遮罩为有色玻璃 (约第 356 行)
  .card-overlay {
    display: block; 
    position: absolute;
    width: 100%;
    height: 100%;
    /* 🎨 关键核心修改：有色玻璃！ */
    /* 我们不使用图片的遮罩，而是直接填充一个非常淡的背景过渡色，让玻璃呈现同色系质感 */
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(175, 202, 244, 0.1) 100%);
  }

  // 修改文字样式 (约第 362 行)
  .card-content {
    position: relative;
    padding: 25px 40px;
    z-index: 1;
    text-align: left;
    /* 🎨 标题：增加文字投影和行高 */
  .card-title {
    font-size: 32px;
    font-weight: 800;
    margin-bottom: 12px;
    text-shadow: none;
    line-height: 1.2;
    max-width: 60%;
    
    /* --- 新增：让标题看起来更有设计感 --- */
    letter-spacing: -1px;  /* 紧凑的字间距更有现代感 */
    display: flex;
    align-items: center;
    
    &::before {
      content: "";
      display: inline-block;
      width: 4px;
      height: 24px;
      margin-right: 12px;
      border-radius: 4px;
      background: currentColor; /* 自动继承标题的颜色 */
      opacity: 0.6;
    }
  }

    /* 🎨 描述文字：调淡并增加行高 */
    .card-desc {
      font-size: 15px;   /* 🎨 调小描述：从 16px 改为 15px */
      opacity: 0.8;
      margin-bottom: 25px;
      line-height: 1.6;
      font-weight: 400; /* 使用普通粗细与标题形成对比 */
      max-width: 60%;
    }

    /* 🎨 修改按钮：不再使用纯色，而是使用渐变边框或半透明色 */
    .card-btn {
      padding: 10px 30px;
      font-size: 14px;
      border-radius: 25px;
      background: rgba(255, 255, 255, 0.8); /* 🎨 半透明白色按钮：增加轻盈感 */
      color: #334455;   /* 按钮文字深灰蓝 */
      border: 1px solid rgba(255, 255, 255, 0.9);
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03); /* 按钮轻阴影 */

      &:hover {
        transform: translateY(-2px); /* 悬停向上微动 */
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
      }
    }
  }
}

/* --- 以下是补充的独有样式 --- */

/* A. 探索岗位卡片 (粉橙色系) */
.explore-card {
  /* 标题颜色与之前保持一致 */
  .card-content .card-title {
    color: #a8b6ff;
  }

  /* 核心彩色插图代码 (使用伪元素 after) */
  &::after {
    content: "";
    position: absolute;
    top: 50%;
    right: -20px; /* 🎨 技巧：让插图稍微超出右边界，更灵动 */
    transform: translateY(-50%);
    width: 280px;  /* 🎨 稍微调大图片，占据更多右半部分 */
    height: 280px;
    
    /* 1. 设置插图背景：直接引入自带颜色的彩色图片 */
    background-image: url("@/assets/explore_color.png"); /* 🎨 请确保路径和文件名正确 */
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;

    /* 2. 核心：设置透明度蒙版 (实现靠近字越淡) */
    /* 我们用 CSS 写一个径向渐变：圆心在右侧，向左侧过渡到完全透明 */
    /* 在 CSS Mask 中，黑色代表可见，透明代表不可见 */
    -webkit-mask-image: radial-gradient(circle at 80% 50%, black 0%, black 30%, rgba(0, 0, 0, 0) 100%);
    mask-image: radial-gradient(circle at 80% 50%, black 0%, black 30%, rgba(0, 0, 0, 0) 100%);
    
    opacity: 0.8; /* 🎨 技巧：静态下保持较低透明度，作为背景装饰，不抢文字 */
    transition: all 0.5s ease;
    z-index: 0;   /* 🎨 关键：确保在内容文字下方 */
  }

  /* 🎨 悬停效果优化 */
  &:hover {
    background-color: rgba(231, 209, 236, 0.15); 
    border-color: rgba(200, 164, 214, 0.4);
    
    /* 悬停时，图片整体变清晰，并向左微动 */
    &::after {
      opacity: 0.6; /* 🎨 调高悬停透明度 */
      transform: translateY(-50%) translateX(-10px);
    }

    /* 按钮变色 */
    .card-btn {
      background: linear-gradient(135deg, #eaaef9 0%, #fad0c4 100%);
      color: #fff;
      border-color: transparent;
    }
  }
}

/* --- B. 开始测评卡片 (蓝绿色系) --- */
.assessment-card {
  /* 标题颜色与之前保持一致 */
  .card-content .card-title {
    color: #b1efbf;
  }

  /* 核心彩色插图代码 (使用伪元素 after) */
  &::after {
    content: "";
    position: absolute;
    top: 50%;
    right: -20px;
    transform: translateY(-50%);
    width: 280px;
    height: 280px;
    
    /* 1. 设置插图背景 */
    background-image: url("@/assets/assessment_color.png"); /* 🎨 请确保路径和文件名正确 */
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;

    /* 2. 核心：透明度蒙版 */
    -webkit-mask-image: radial-gradient(circle at 70% 50%, black 0%, black 40%, rgba(0, 0, 0, 0) 100%);
    mask-image: radial-gradient(circle at 70% 50%, black 0%, black 40%, rgba(0, 0, 0, 0) 100%);
    opacity: 0.8;
    transition: all 0.5s ease;
    z-index: 0;
  }

  /* 🎨 悬停效果优化 */
  &:hover {
    background-color: rgba(72, 187, 98, 0.699);
    border-color: rgba(177, 239, 191, 0.4);

    &::after {
      opacity: 0.6;
      transform: translateY(-50%) translateX(-10px);
    }

    /* 按钮变色 */
    .card-btn {
      background: linear-gradient(135deg, #afcaf4 0%, #b1efbf 100%);
      color: #fff;
      border-color: transparent;
    }
  }
}

/* B. 开始测评卡片 (蓝绿色系) */
.assessment-card {
  /* 标题变色 */
  .card-content .card-title {
    color: #88d098; /* 呼应背景的 #b1efbf */
  }

  /* 悬停时：卡片背景呈现淡淡的蓝绿色 */
  &:hover {
    background-color: rgba(177, 239, 191, 0.15);
    border-color: rgba(177, 239, 191, 0.4);

    .card-btn {
      background: linear-gradient(135deg, #afcaf4 0%, #b1efbf 100%);
      color: #fff;
      border-color: transparent;
    }
  }
}

/* 右列：登录面板 */
/* ========================================================== */
/* 🎨 登录面板美化：AI 科技感 + 毛玻璃材质 */
/* ========================================================== */

/* ========================================================== */
/* 🎨 登录面板美化：AI 科技感 + 毛玻璃材质 */
/* ========================================================== */


.auth-card {
  border-radius: 24px !important;
  background: rgba(255, 255, 255, 0.65) !important;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.05);

  .login-form {
    padding: 20px;

    /* 顶部标题区域 */
    .form-header {
      text-align: center;
      margin-bottom: 30px;
      
      .user-avatar {
        background: linear-gradient(135deg, #409EFF 0%, #667eea 100%);
        box-shadow: 0 4px 15px rgba(64, 158, 255, 0.3);
        margin-bottom: 12px;
      }
      .welcome-text {
        display: block;
        font-size: 22px;
        font-weight: 700;
        color: #303133;
      }
      .sub-text {
        font-size: 13px;
        color: #909399;
        margin-top: 6px;
      }
    }

    /* 登录按钮 */
    .submit-btn {
      width: 100%;
      height: 44px;
      border-radius: 12px;
      background: linear-gradient(135deg, #409EFF 0%, #0076FF 100%);
      border: none;
      font-weight: 600;
      margin-top: 10px;
      transition: all 0.3s;
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(64, 158, 255, 0.3);
      }
    }

    /* 底部页脚区域 - 解决“混乱”的关键 */
    .form-footer {
      margin-top: 25px;
      display: flex;
      flex-direction: column;
      align-items: center; /* 居中所有内容 */

      .register-tip {
        font-size: 12px; /* 🎨 缩小字号 */
        color: #909399;
        margin-bottom: 20px;
        
        .register-link {
          color: #409EFF;
          font-weight: 500;
          margin-left: 4px;
          cursor: pointer;
          &:hover { text-decoration: underline; }
        }
      }

      .divider-text {
        width: 100%;
        font-size: 12px; /* 🎨 缩小字号 */
        color: #c0c4cc;
        text-align: center;
        margin-bottom: 15px;
        position: relative;
        
        /* 辅助线装饰 */
        &::before, &::after {
          content: "";
          position: absolute;
          top: 50%;
          width: 25%;
          height: 1px;
          background: rgba(0, 0, 0, 0.06);
        }
        &::before { left: 5%; }
        &::after { right: 5%; }
      }

      /* 第三方图标 */
      .social-icons {
        display: flex;
        justify-content: center; /* 🌟 核心：让三个圆圈在登录面板水平居中 */
        gap: 18px;               /* 圆圈之间的间距 */
        width: 100%;             /* 占满宽度以确保居中基准 */
        
        .icon-item {
          width: 38px;           /* 稍微调大一点点，更精致 */
          height: 38px;
          border-radius: 50%;
          background: #fff;
          border: 1px solid rgba(0, 0, 0, 0.05);
          display: flex;
          align-items: center;   /* 图标垂直居中 */
          justify-content: center; /* 图标水平居中 */
          color: #606266;
          transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
          cursor: pointer;
          
          /* 🌟 对内部 Element Plus 图标的微调 */
          .el-icon {
            font-size: 18px; 
          }
          
          &:hover {
            color: #409EFF;
            border-color: #409EFF;
            transform: translateY(-3px) scale(1.1); /* 悬停时轻微上浮 */
            background: rgba(64, 158, 255, 0.04);
            box-shadow: 0 4px 10px rgba(64, 158, 255, 0.1);
          }
        }
      }
    }
  }
}


// ========== 4. 动画定义 ==========
@keyframes gradientBG {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* ========================================================== */
/* 🌌 数据粒子放射引力场（保留自原热门岗位板块） */
/* ========================================================== */
.particle-section {
  max-width: 1600px;
  margin: 120px auto 120px;
  padding: 0 40px;
  position: relative;
  z-index: 5;
  overflow: visible;
}

/* 🌟 核心：数据粒子放射板块 */
.data-particle-field {
  position: relative;
  width: 100%;
  height: 700px;
  margin-top: -100px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  perspective: 1000px;

  .bg-canvas {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: -3;
    pointer-events: none;
    background: radial-gradient(circle at center, #f8faff 0%, transparent 50%);
  }

  .connection-lines {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: -1;
    pointer-events: none;
    overflow: visible;

    .orbit-ring {
      transform-origin: center;
      animation: rotateRing 60s linear infinite;
    }

    path {
      animation: pulse-dash 2s linear infinite;
    }
  }

  &::before {
    content: "";
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 100%;
    height: 100%;
    z-index: -2;
    background:
      radial-gradient(circle at 45% 25%, rgba(202, 229, 253, 0.654) 0%, transparent 35%),
      radial-gradient(circle at 60% 65%, rgba(201, 163, 244, 0.267) 0%, transparent 30%);
    filter: blur(10px);
    animation: quantumGlow 15s ease-in-out infinite alternate;
  }

  &::after {
    content: "";
    position: absolute;
    top: -100px; left: 0; width: 100%; height: calc(100% + 200px);
    z-index: -1;
    background-image:
      radial-gradient(circle at 1.5px 1.5px, rgba(64, 158, 255, 0.15) 1px, transparent 0);
    background-size: 40px 40px;
    mask-image: radial-gradient(circle at center, black 30%, transparent 90%);
    opacity: 0.6;
    animation: quantumParticles 25s linear infinite;
  }
}

.post-sphere {
  position: absolute;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;

  background: rgba(255, 255, 255, 0.4) !important;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.6) !important;

  box-shadow:
    inset 0 1px 1px rgba(255, 255, 255, 0.8),
    0 10px 40px -10px rgba(177, 138, 255, 0.15) !important;

  .label {
    font-size: 13px; font-weight: 700; color: #303133; text-align: center;
    padding: 10px;
    transition: color 0.3s;
  }

  &:hover {
    background: rgba(255, 255, 255, 0.8) !important;
    box-shadow: 0 0 35px rgba(0, 219, 230, 0.3) !important;
    z-index: 20;
    .label { color: #409EFF; }
  }
}

@keyframes pulse-dash {
  to { stroke-dashoffset: -20; }
}
@keyframes rotateRing {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.center-text-block {
  text-align: center;
  z-index: 10;
  color: #334455;

  .small-title {
    font-size: 14px; color: #90a4ae; font-weight: 500; margin-bottom: 8px;
    letter-spacing: 2px;
  }
  .big-data {
    font-size: 52px; font-weight: 800; line-height: 1.2; margin-bottom: 12px;
    letter-spacing: -2px;

    .highlight {
      background: linear-gradient(135deg, #409EFF 0%, #0076FF 100%);
      -webkit-background-clip: text;
      background-clip: text;
      -webkit-text-fill-color: transparent;
      font-weight: 900;
    }
  }
  .ai-analysis {
    font-size: 26px; font-weight: 600; color: rgba(51, 68, 85, 0.7);
    text-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
  }
}

.post-sphere {
  position: absolute;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;

  background: rgba(255, 255, 255, 0.15) !important;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.05) !important;
  cursor: pointer;
  overflow: hidden;

  box-shadow:
    0 8px 32px 0 rgba(31, 38, 135, 0.1),
    inset 0 0 10px rgba(255, 255, 255, 0.2);

  color: #fff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

  .label {
    font-size: 13px; font-weight: 600; color: #409EFF; text-align: center;
    padding: 10px;
  }

  &:hover {
    background: rgba(64, 158, 255, 0.3) !important;
  border: 1px solid rgba(64, 158, 255, 0.5);
  transform: scale(1.2) translateY(-5px) !important;
  box-shadow: 0 0 20px rgba(64, 158, 255, 0.4);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
  }
}

.post-sphere::before {
  content: "";
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    45deg,
    transparent,
    rgba(255, 255, 255, 0.1),
    transparent
  );
  transform: rotate(45deg);
  animation: shine 4s infinite linear;
}

@keyframes shine {
  0% { transform: translateX(-100%) rotate(45deg); }
  100% { transform: translateX(100%) rotate(45deg); }
}

.sphere-1 {
  width: 90px; height: 90px;
  top: 18%; left: 28%;
  transform: translateZ(50px);
  background: linear-gradient(135deg, #f9d1c0 0%, #fcfbe3 100%) !important;
}

.sphere-2 {
  width: 100px; height: 100px;
  top: 60%; left: 20%;
  transform: translateZ(-20px);
  background: linear-gradient(135deg, #fffbeb 0%, #dffec7 100%) !important;
}

.sphere-3 {
  width: 120px; height: 120px;
  top: 10%; left: 45%;
  transform: translateZ(100px);
  background: linear-gradient(135deg, #abcff6 0%, #c4efeb 100%) !important;
}

.sphere-4 {
  width: 85px; height: 85px;
  top: 18%; left: 75%;
  transform: translateZ(30px);
  background: linear-gradient(135deg, #fef2f2 0%, #fee4fa 100%) !important;
}

.sphere-5 {
  width: 95px; height: 95px;
  top: 60%; left: 78%;
  transform: translateZ(10px);
  background: linear-gradient(135deg, #f0f9eb 0%, #d8f3f3 100%) !important;
}

.sphere-6 {
  width: 75px; height: 75px;
  top: 35%; left: 10%;
  transform: translateZ(-50px);
}

.sphere-7 {
  width: 80px; height: 80px;
  top: 38%; left: 85%;
  transform: translateZ(-40px);
}

.sphere-8 {
  width: 90px; height: 90px;
  top: 65%; left: 50%;
  transform: translateZ(-10px);
}

.sphere-9 {
  width: 70px; height: 70px;
  top: 80%; left: 52%;
  transform: translateZ(-30px);
  opacity: 0.7 !important;
}

.sphere-10 {
  width: 65px; height: 65px;
  top: 8%; left: 8%;
  transform: translateZ(-50px);
  opacity: 0.6 !important;
}

.sphere-11 {
  width: 72px; height: 72px;
  top: 50%; left: 92%;
  transform: translateZ(-60px);
  opacity: 0.5 !important;
}

.sphere-12 {
  width: 60px; height: 60px;
  top: 2%; left: 62%;
  transform: translateZ(-80px);
  opacity: 0.4 !important;
}

.sphere-13 {
  width: 75px; height: 75px;
  top: 78%; left: 28%;
  transform: translateZ(-40px);
  opacity: 0.7 !important;
}

.sphere-14 {
  width: 68px; height: 68px;
  top: 75%; left: 68%;
  transform: translateZ(-55px);
  opacity: 0.6 !important;
}

.sphere-15 {
  width: 70px; height: 70px;
  top: 50%; left: 4%;
  transform: translateZ(-70px);
  opacity: 0.5 !important;
}

.sphere-16 {
  width: 62px; height: 62px;
  top: 3%; left: 32%;
  transform: translateZ(-90px);
  opacity: 0.4 !important;
}

@keyframes floatRandomly {
  0% { transform: translateY(0) rotate(0deg) translateZ(0); }
  33% { transform: translateY(-35px) translateX(-10px) rotate(6deg) translateZ(10px); }
  66% { transform: translateY(20px) translateX(15px) rotate(-5deg) translateZ(-5px); }
  100% { transform: translateY(0) rotate(0deg) translateZ(0); }
}

@keyframes Blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

@keyframes quantumFlow {
  0% { transform: rotate(0deg) scale(1); }
  50% { transform: rotate(180deg) scale(1.1); }
  100% { transform: rotate(360deg) scale(1); }
}

@keyframes particleDrift {
  0% { transform: translate(0, 0); opacity: 0.3; }
  50% { transform: translate(-20px, 20px); opacity: 0.6; }
  100% { transform: translate(0, 0); opacity: 0.3; }
}

@keyframes quantumGlow {
  0% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
  100% { opacity: 1; transform: translate(-50%, -50%) scale(1.2); }
}

@keyframes quantumParticles {
  from { background-position: 0 0; }
  to { background-position: 0 1000px; }
}

/* ========================================================== */
/* 🔥 5. 实训任务预览 · 横向展开画廊（Accordion）               */
/* ========================================================== */
.task-gallery-section {
  max-width: 1400px;
  margin: -100px auto 80px;
  padding: 0 40px;
  position: relative;
  z-index: 5;
}

.gallery-header {
  display: flex;
  align-items: baseline;
  gap: 14px;
  margin-bottom: 34px;
  padding-left: 10px;
  border-left: 4px solid #409EFF;

  .section-title {
    margin: 0;
    font-size: 26px;
    font-weight: 800;
    color: #334455;
    letter-spacing: 1px;
  }

  .gallery-sub {
    font-size: 12px;
    font-weight: 600;
    color: #94a3b8;
    letter-spacing: 1.5px;
  }
}

/* ---- Accordion Gallery ---- */
.accordion-gallery {
  display: flex;
  gap: 10px;
  height: 460px;
  position: relative;
  perspective: 1200px;
}

.accordion-card {
  flex: 0 0 auto;
  width: 0;
  min-width: 0;
  overflow: hidden;
  cursor: pointer;
  border-radius: 16px;
  position: relative;
  will-change: transform, width;
}

.accordion-card__inner {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  border-radius: 16px;
}

.accordion-card__bg {
  width: 100%;
  height: 100%;
  position: relative;
  backdrop-filter: blur(14px) saturate(160%);
  -webkit-backdrop-filter: blur(14px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 16px;
  opacity: 0.55;
  will-change: opacity, filter;
}

.accordion-card__overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.12);
  pointer-events: none;
  opacity: 0;
  border-radius: 16px;
}

.accordion-card__content {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
  text-align: left;
  padding: 40px 24px 22px;
  background: linear-gradient(transparent 0%, rgba(255, 255, 255, 0.9) 100%);
  color: #334455;
  opacity: 1;
  will-change: transform, opacity;
}

.accordion-card__badge {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.55);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  color: #409EFF;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
  border: 1px solid rgba(64, 158, 255, 0.18);
}

.accordion-card__progress {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.35);
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 5px;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.accordion-card__progress .progress-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.accordion-card__progress.status-done { color: #67C23A; }
.accordion-card__progress.status-done .progress-dot { background: #67C23A; box-shadow: 0 0 6px rgba(103, 194, 58, 0.6); }
.accordion-card__progress.status-doing { color: #409EFF; }
.accordion-card__progress.status-doing .progress-dot { background: #409EFF; box-shadow: 0 0 6px rgba(64, 158, 255, 0.6); animation: pulse 1.6s infinite; }
.accordion-card__progress.status-todo { color: #909399; }
.accordion-card__progress.status-todo .progress-dot { background: #b0b3b8; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.35; }
}

.accordion-card__thumb {
  position: absolute;
  top: 310px;
  right: 80px;
  width: 148px;
  height: 148px;
  object-fit: cover;
  z-index: 2;
  pointer-events: none;
  will-change: filter;
}

.accordion-card__title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #1e293b;
  max-width: 100%;
}

.accordion-card__desc {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 10px;
  line-height: 1.5;
  max-width: 100%;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.accordion-card__steps {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 3px;
  margin-bottom: 4px;
}

.accordion-card__step {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12.5px;
  opacity: 0.9;
  white-space: nowrap;
  color: #475569;
}

.accordion-card__step .step-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: rgba(64, 158, 255, 0.55);
  flex-shrink: 0;
}

.accordion-card__comment {
  font-size: 12px;
  color: #64748b;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  max-width: 100%;
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.accordion-card__comment .comment-label {
  font-weight: 600;
  color: #409EFF;
  font-style: normal;
  flex-shrink: 0;
}

/* ---- 响应式 ---- */
@media (max-width: 768px) {
  .task-gallery-section { padding: 0 20px; }
  .accordion-gallery { height: 320px; }
  .accordion-card { border-radius: 10px; }
  .accordion-card__inner { border-radius: 10px; }
  .accordion-card__content { padding: 18px 12px; }
  .accordion-card__title { font-size: 15px; }
  .accordion-card__desc { font-size: 12px; }
  .accordion-card__step { font-size: 12px; }
  .accordion-card__comment { font-size: 11px; }
  .accordion-card__progress { font-size: 11px; padding: 2px 9px; }
  .accordion-card__thumb { width: 40px; height: 40px; top: 10px; right: 72px; }
}

/* ========================================================== */
/* 右侧面板 right-panel 完整样式                            */
/* ========================================================== */

.roadmap-focus-card {
  background: rgba(255, 255, 255, 0.85) !important;
  backdrop-filter: blur(15px);
  border-radius: 24px !important;
  border: 1px solid rgba(64, 158, 255, 0.15) !important;
  height: 570px;
  display: flex;
  flex-direction: column;
}

.roadmap-focus-card :deep(.el-card__body) {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px 22px !important;
}

/* 顶部状态栏 */
.rp-status-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 16px;

  .pulse-dot {
    width: 6px;
    height: 6px;
    background: #409eff;
    border-radius: 50%;
    box-shadow: 0 0 8px #409eff;
    animation: blink 1.5s infinite;
  }
}

/* 加载态 */
.rp-loading {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 20px 0;
}

/* ---- 空态 ---- */
.rp-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 20px;

  .rp-empty-illustration {
    width: 110px;
    height: 110px;
    animation: rpFloat 4s ease-in-out infinite;
    border-radius: 50%; /* 确保阴影的外形是完美的圆形 */
    box-shadow: 0 8px 24px rgba(149, 215, 247, 0.777); /* 核心阴影代码 */
    svg { width: 100%; height: 100%; }
  }

  .rp-empty-title {
    font-size: 17px;
    font-weight: 700;
    color: #303133;
  }

  .rp-empty-desc {
    font-size: 13px;
    color: #909399;
    text-align: center;
    line-height: 1.7;
  }

  .rp-empty-btn {
    margin-top: 4px;
    padding: 10px 28px;
    font-size: 14px;
    border-radius: 20px;
    background: linear-gradient(135deg, #98c8f7 0%, #f0cbe5 100%) !important;
    border: none !important;
    color: #fffff8 !important;
    box-shadow: 0 4px 15px rgba(64, 158, 255, 0.3);
    transition: all 0.3s;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(64, 158, 255, 0.4);
    }
  }
}

@keyframes rpFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

/* ---- 有数据内容区 ---- */
.rp-content {
  flex: 1;
  position: relative;
  overflow: hidden;
}

/* 画像概览页 */
.rp-page {
  padding: 4px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow-y: auto;
  background: #fff;
  border-radius: 14px;
}

/* 用户头像行 + 综合评分 */
.rp-user-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-bottom: 12px;
  border-bottom: 1px dashed #ebeef5;
}

.rp-user-info {
  flex: 1;
  min-width: 0;
}

.rp-user-name {
  font-size: 15px;
  font-weight: 700;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.rp-user-sub {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rp-score-badge {
  text-align: center;
  flex-shrink: 0;
}

.rp-score-num {
  font-size: 32px;
  font-weight: 900;
  line-height: 1;
  background: linear-gradient(135deg, #409EFF 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.rp-score-label {
  font-size: 10px;
  color: #909399;
  margin-top: 2px;
}

/* 七维度网格 */
/* 能力雷达图 */
.rp-radar-chart {
  background: rgba(64, 158, 255, 0.04);
  border-radius: 10px;
  padding: 4px;
}

.radar-chart {
  width: 100%;
  height: 150px;
}

/* 能力缺口词云 */
.rp-gap-cloud {
  margin-top: 4px;
}

.cloud-body {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 8px 14px;
  min-height: 46px;
  padding: 6px 4px 2px;
}

.cloud-tag {
  font-weight: 600;
  cursor: default;
  transition: all 0.2s;

  &:hover {
    transform: translateY(-2px);
  }

  &.danger { color: #f56c6c; }
  &.warning { color: #e6a23c; }
  &.info { color: #909399; }
}

/* 能力缺口词云空态 */
.rp-tasks-empty {
  font-size: 12px;
  color: #c0c4cc;
  text-align: center;
  padding: 20px 0;
}

/* ---- 第二页：能力缺口 + Agent 建议 ---- */
.rp-gap-title {
  font-size: 14px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 4px;
}

/* 底部按钮 */
.rp-bottom-btn {
  width: 100%;
  margin-top: auto;
  font-size: 13px;
  background: transparent !important;
  color: #409eff !important;
  border-color: #409eff !important;

  &:hover {
    background: rgba(64, 158, 255, 0.05) !important;
  }
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.7); }
  70% { box-shadow: 0 0 0 10px rgba(64, 158, 255, 0); }
  100% { box-shadow: 0 0 0 0 rgba(64, 158, 255, 0); }
}
@keyframes blink { 50% { opacity: 0.3; } }



.home-footer {
  padding: 5px;
  text-align: center;
  color: #909399;
  border-top: 1px solid #e4e7ed;
  background: #fff;
}

</style>
