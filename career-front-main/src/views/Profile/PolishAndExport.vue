<template>
  <div class="feedback-page">
    <!-- ============ 一、顶部指标栏 ============ -->
    <div class="metrics-row">
      <div class="feedback-title">
        <h2 class="ft-cn">反馈与复盘中心</h2>
        <span class="ft-en">FEEDBACK &amp; REVIEW</span>
      </div>
      <div class="metrics-bar">
        <div class="metric-card" v-for="m in metrics" :key="m.label">
          <div class="metric-icon" :style="{ background: m.bg }">
            <el-icon><component :is="m.icon" /></el-icon>
          </div>
          <div class="metric-info">
            <span class="metric-value">{{ m.value }}</span>
            <span class="metric-label">{{ m.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ============ 二、左栏 + 三、右栏 ============ -->
    <div class="main-row">
      <!-- 左栏 -->
      <div class="left-col">
        <!-- 1. 薄弱点聚合分析 -->
        <div class="weakness-card glass-card">
          <div class="wc-header">
            <span class="wc-title">薄弱点聚合分析</span>
            <el-tag size="small" class="wc-tag" effect="plain">高频薄词云</el-tag>
          </div>
          <div class="wc-body">
            <el-tag
              v-for="tag in weakTags"
              :key="tag.text"
              :type="tag.highlight ? 'primary' : 'info'"
              :effect="tag.highlight ? 'dark' : 'plain'"
              class="wc-tag-item"
              :class="{ 'is-highlight': tag.highlight }"
              size="small"
            >{{ tag.text }}</el-tag>
          </div>
        </div>

        <!-- 2. 7 天反馈评级趋势 -->
        <div class="trend-card glass-card">
          <div class="tc-header">
            <span class="tc-title">7 天反馈评级趋势</span>
          </div>
          <div class="tc-body">
            <div ref="trendChartRef" class="trend-chart"></div>
          </div>
        </div>
      </div>

      <!-- 右栏 -->
      <div class="right-col">
        <div class="timeline-card glass-card">
          <div class="timeline-banner">反馈时间线</div>
          <div class="timeline-body">
            <div
              v-for="(evt, idx) in timelineEvents"
              :key="evt.id"
              class="tl-item"
              @click="showEvent(evt)"
            >
              <div class="tl-dot-row">
                <div class="tl-dot" :class="{ 'is-active': activeEvent?.id === evt.id }">
                  <span class="tl-num">{{ idx + 1 }}</span>
                </div>
                <div v-if="idx < timelineEvents.length - 1" class="tl-line"></div>
              </div>
              <div class="tl-content">
                <span class="tl-date">{{ evt.date }} {{ evt.weekday }}</span>
                <span class="tl-title">{{ evt.title }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ============ 悬停浮窗（居中圆角卡片） ============ -->
    <div v-if="activeEvent" class="event-overlay" @click="activeEvent = null">
      <div class="event-popup" @click.stop>
        <div class="popup-header">
          <span class="popup-title">{{ activeEvent.title }}</span>
          <el-icon class="popup-close" @click="activeEvent = null"><Close /></el-icon>
        </div>
        <div class="popup-body">
          <div class="popup-section">
            <div class="popup-section-label">问题定位</div>
            <div class="popup-section-text">{{ activeEvent.problem }}</div>
          </div>
          <div class="popup-section">
            <div class="popup-section-label">改进建议</div>
            <div class="popup-section-text">{{ activeEvent.suggestion }}</div>
          </div>
          <div class="popup-section">
            <div class="popup-section-label">下一步练习</div>
            <div class="popup-section-text">{{ activeEvent.next }}</div>
          </div>
          <div class="popup-section">
            <div class="popup-section-label">薄弱分析</div>
            <div class="popup-section-text">
              <template v-if="activeEvent.weakness">{{ activeEvent.weakness }}</template>
              <template v-else>暂无薄弱分析，完成任务后自动生成</template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import {
  Document, EditPen, Warning, ChatDotRound,
  DataAnalysis, TrendCharts, Close, ArrowRight
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '@/api/client'

// --- 指标数据（从后端拉取）---
const metrics = ref([
  { icon: Document, value: '--', label: '总提交次数', bg: 'rgba(64, 158, 255, 0.1)' },
  { icon: EditPen, value: '--', label: '平均匹配评分', bg: 'rgba(16, 185, 129, 0.1)' },
  { icon: Warning, value: '--', label: '最大薄弱维度', bg: 'rgba(245, 158, 11, 0.1)' },
  { icon: ChatDotRound, value: '--', label: '连续活跃天数', bg: 'rgba(139, 92, 246, 0.1)' },
])

// --- 薄弱点标签 ---
const weakTags = ref([])

// --- LLM 薄弱分析（每条含 problem/suggestion/next）---
const llmFeedback = ref([])

// --- 7 天趋势图 ---
const trendChartRef = ref(null)
let trendChart = null

const trendXData = reactive(['周一', '周二', '周三', '周四', '周五', '周六', '周日'])
const trendThisWeek = reactive([0, 0, 0, 0, 0, 0, 0])

function buildChartOption() {
  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: 'rgba(255,255,255,0.3)',
      borderRadius: 12,
      boxShadow: '0 8px 24px rgba(0,0,0,0.08)',
      axisPointer: { type: 'cross' },
    },
    legend: {
      data: ['本周完成数'],
      bottom: 0,
      itemWidth: 12,
      itemHeight: 8,
      textStyle: { color: '#94a3b8', fontSize: 11 },
    },
    grid: { left: 36, right: 20, top: 24, bottom: 40 },
    xAxis: {
      type: 'category',
      data: trendXData.slice(),
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      axisLabel: { color: '#94a3b8', fontSize: 11 },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      min: 0,
      splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
      axisLabel: { color: '#94a3b8', fontSize: 11 },
    },
    series: [{
      name: '本周完成数',
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { color: '#70a1ff', width: 2 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(112, 161, 255, 0.25)' },
          { offset: 1, color: 'rgba(112, 161, 255, 0.02)' },
        ]),
      },
      data: trendThisWeek.slice(),
    }],
  }
}

const initChart = () => {
  if (!trendChartRef.value) return
  trendChart?.dispose()
  trendChart = echarts.init(trendChartRef.value)
  trendChart.setOption(buildChartOption())
  setTimeout(() => trendChart?.resize(), 50)
}

const handleResize = () => trendChart?.resize()

// --- 时间线点击控制 ---
const activeEvent = ref(null)
const showEvent = (evt) => { activeEvent.value = evt }

const timelineEvents = ref([])

// --- Fetch real data from backend ---
async function fetchFeedback() {
  try {
    const { data } = await api.get('/feedback')
    if (!data.data) return
    const d = data.data

    // Metrics
    if (d.metrics) {
      metrics.value = metrics.value.map((m, i) => ({
        ...m,
        value: d.metrics[i]?.value || '--',
      }))
    }

    // Weak tags
    if (d.weak_tags) {
      weakTags.value = d.weak_tags.filter(t => t.highlight).concat(
        d.weak_tags.filter(t => !t.highlight)
      )
    }

    // LLM 薄弱分析（按 task_id 索引，弹窗匹配）
    const fbByTask = {}
    if (d.llm_feedback) {
      llmFeedback.value = d.llm_feedback
      d.llm_feedback.forEach(fb => {
        if (fb.task_id) fbByTask[fb.task_id] = fb
      })
    }

    // Timeline：合并任务专属反馈
    if (d.events) {
      timelineEvents.value = d.events.map((e, i) => {
        const fb = fbByTask[e.task_id] || {}
        return {
          id: i + 1,
          date: e.date,
          weekday: e.weekday,
          title: e.title,
          type: e.type,
          status: e.status,
          task_id: e.task_id,
          problem: fb.problem || `任务「${e.title}」状态变更为${e.statusLabel || e.status}`,
          suggestion: fb.suggestion || '完成该任务后，AI将根据表现给出具体建议',
          next: fb.next || '持续练习，巩固该任务涉及的技能点',
          weakness: fb.weakness || '',
        }
      })
    }

    // Trend chart
    if (d.trend) {
      d.trend.forEach((v, i) => { if (i < 7) trendThisWeek[i] = v })
      initChart()
    }
  } catch (err) {
    console.error('[Feedback] fetch failed:', err)
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  fetchFeedback()
  initChart()
})
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
})
</script>

<style scoped>
.feedback-page {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 10px;
  max-width: 1200px;
  margin: 0 auto;
}

.glass-card {
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(20px) saturate(1.1);
  -webkit-backdrop-filter: blur(20px) saturate(1.1);
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

/* ========== 一、顶部指标栏 ========== */
.metrics-row {
  display: flex;
  align-items: center;
  gap: 28px;
  margin-bottom: 20px;
  flex-shrink: 0;
}

.feedback-title {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding-left: 4px;
}
.ft-cn {
  margin: 0;
  font-size: 30px;
  font-weight: 800;
  color: #1e293b;
  letter-spacing: 0.5px;
  white-space: nowrap;
}
.ft-en {
  font-size: 10px;
  font-weight: 600;
  color: #94a3b8;
  letter-spacing: 2px;
  white-space: nowrap;
}

.metrics-bar {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.metric-card {
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(20px) saturate(1.1);
  -webkit-backdrop-filter: blur(20px) saturate(1.1);
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 18px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
  padding: 18px 22px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.2s;
}
.metric-card:hover {
  transform: translateY(-2px);
}

.metric-icon {
  width: 50px;
  height: 50px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.metric-icon .el-icon {
  font-size: 22px;
  color: #475569;
}

.metric-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.metric-value {
  font-size: 25px;
  font-weight: 800;
  color: #1e293b;
  line-height: 1.2;
}
.metric-label {
  font-size: 12px;
  color: #94a3b8;
}

/* ========== 二、三：左右两栏 ========== */
.main-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  align-items: stretch;
  flex: 1;
  min-height: 0;
}

.left-col {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 0;
}

/* ===== 薄弱点聚合分析 ===== */
.weakness-card {
  padding: 0;
}
.wc-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.2);
}
.wc-title {
  font-weight: 600;
  color: #1e293b;
  font-size: 16px;
}
.wc-tag {
  border-radius: 12px;
  font-size: 11px;
  background: rgba(255, 255, 255, 0.5) !important;
  border-color: rgba(255, 255, 255, 0.3) !important;
  color: #667eea !important;
}
.wc-body {
  padding: 22px 24px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.wc-tag-item {
  border-radius: 10px;
  font-size: 13px;
  padding: 6px 14px;
  transition: transform 0.2s;
}
.wc-tag-item:hover {
  transform: scale(1.05);
}
.wc-tag-item.is-highlight {
  font-weight: 700;
  background: #667eea !important;
  border-color: #667eea !important;
  color: #fff !important;
}

/* ===== 7 天趋势图 ===== */
.trend-card {
  padding: 0;
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}
.tc-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.2);
}
.tc-title {
  font-weight: 600;
  color: #1e293b;
  font-size: 16px;
}
.tc-body {
  padding: 12px 12px 0;
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.trend-chart {
  flex: 1;
  width: 100%;
  min-height: 240px;
}

/* ===== 右栏：时间线 ===== */
.right-col {
  display: flex;
  align-items: stretch;
  min-height: 0;
}

.timeline-card {
  padding: 0;
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  min-height: 540px;
}

.timeline-banner {
  flex-shrink: 0;
}
.timeline-banner {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(255, 255, 255, 0.3));
  padding: 18px 24px;
  font-weight: 700;
  color: #1e293b;
  font-size: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px 20px 0 0;
  text-align: center;
}

.timeline-body {
  padding: 14px 24px 14px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.tl-item {
  display: flex;
  gap: 16px;
  cursor: pointer;
  padding: 8px 0;
  flex: 1;
  transition: background 0.2s;
  border-radius: 8px;
}
.tl-item:hover {
  background: rgba(255, 255, 255, 0.5);
}

.tl-dot.is-active {
  background: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2);
}

.tl-dot-row {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  width: 38px;
}
.tl-dot {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}
.tl-num {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
}
.tl-line {
  width: 2px;
  flex: 1;
  min-height: 24px;
  background: linear-gradient(to bottom, #e2e8f0, transparent);
}
.tl-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-top: 6px;
  min-width: 0;
}
.tl-date {
  font-size: 12px;
  color: #94a3b8;
}
.tl-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.4;
}

/* ========== 悬停浮窗 ========== */
.event-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.12);
  cursor: pointer;
  animation: fadeIn 0.2s ease-out;
}
.event-popup {
  pointer-events: auto;
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  width: 90vw;
  max-width: 640px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  animation: popIn 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}
.popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  border-bottom: 1px solid #f1f5f9;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.06), rgba(255, 255, 255, 0.3));
}
.popup-title {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
}
.popup-close {
  font-size: 18px;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px;
  border-radius: 8px;
  transition: all 0.2s;
}
.popup-close:hover {
  background: #f1f5f9;
  color: #475569;
}
.popup-body {
  padding: 20px 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.popup-section-label {
  font-size: 13px;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.popup-section-label::before {
  content: '';
  width: 4px;
  height: 14px;
  background: #667eea;
  border-radius: 2px;
  flex-shrink: 0;
}
.popup-section-text {
  font-size: 14px;
  color: #334155;
  line-height: 1.7;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes popIn {
  from { opacity: 0; transform: scale(0.92) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

@media (max-width: 768px) {
  .metrics-row {
    flex-direction: column;
    align-items: stretch;
    gap: 14px;
  }
  .metrics-bar { grid-template-columns: repeat(2, 1fr); }
  .main-row { grid-template-columns: 1fr; }
  .timeline-body { max-height: 400px; }
}
</style>