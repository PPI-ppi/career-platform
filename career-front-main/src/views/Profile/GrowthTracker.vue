<template>
  <div class="growth-tracking-center">
    <template v-if="pageLoading">
      <div class="loading-state">加载中...</div>
    </template>

    <template v-else-if="todoList.length === 0">
      <div class="empty-state">请先完成能力对标并锁定目标岗位后查看实训任务</div>
    </template>

    <template v-else>
      <!-- ============ 区域一：顶部进度区 ============ -->
      <div class="progress-section glass-card">
        <div class="progress-left">
          <div class="goal-block">
            <span class="goal-label">
              <el-icon><Aim /></el-icon>
              当前阶段大目标
            </span>
            <span class="goal-text">{{ currentGoal }}</span>
          </div>
          <div class="encouragement">
            <el-icon class="enc-icon"><MagicStick /></el-icon>
            <span>{{ encouragement }}</span>
          </div>
        </div>
        <div class="progress-right">
          <el-progress
            type="circle"
            :percentage="progressPercentage"
            :width="88"
            :stroke-width="8"
            color="#70a1ff"
            :show-text="false"
          />
          <div class="progress-num">
            <strong>{{ completedCount }}</strong>
            <span class="total">/ {{ totalCount }}</span>
          </div>
          <div class="progress-label">任务进度</div>
        </div>
      </div>

      <!-- ============ 区域二：中部任务拆解列表 ============ -->
      <div class="tasks-section glass-card">
        <div class="section-header">
          <div class="section-title">
            <el-icon><List /></el-icon>
            本周任务拆解
          </div>
          <span class="section-subtitle">点击任务卡片，AI 实训导师带你逐项攻克</span>
        </div>

        <div class="task-cards-horizontal">
          <div
            v-for="(task, idx) in todoList"
            :key="task.id"
            class="task-card"
            :class="{
              'is-active': selectedTask && selectedTask.id === task.id,
              'is-completed': task.status === 'completed',
              'is-in-progress': task.status === 'in_progress'
            }"
            @click="selectTask(task)"
          >
            <div class="task-top-row">
              <span class="task-number">{{ String(idx + 1).padStart(2, '0') }}</span>
              <span class="task-status" :class="`st-${task.status}`">
                {{ statusIcon(task.status) }}{{ statusLabel(task.status) }}
              </span>
            </div>
            <div class="task-name">{{ task.text }}</div>
            <div class="task-desc">{{ task.desc || '点击卡片开始实训' }}</div>
            <div class="task-meta">
              <span class="meta-tag"><el-icon><Timer /></el-icon> {{ task.time }}min</span>
              <span class="meta-tag"><el-icon><StarFilled /></el-icon> {{ task.difficulty }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ============ 区域三：底部执行聊天区 ============ -->
      <div v-if="selectedTask" class="chat-section glass-card">
        <div class="section-header">
          <div class="section-title">
            <el-icon><MagicStick /></el-icon>
            实训导师 · {{ selectedTask.text }}
          </div>
          <el-button
            v-if="selectedTask.status !== 'completed'"
            size="small"
            type="primary"
            plain
            @click="completeTask(selectedTask)"
          >
            <el-icon><CircleCheck /></el-icon>
            标记为已完成
          </el-button>
          <el-tag v-else size="small" type="success" effect="plain">✅ 已完成</el-tag>
        </div>

        <div class="chat-area">
          <div class="chat-messages" ref="chatMessagesRef">
            <!-- 任务详情系统消息 -->
            <div v-if="selectedTask" class="bot-msg-wrapper">
              <div class="bot-avatar-mini"><el-icon><MagicStick /></el-icon></div>
              <div class="bot-content">
                <span class="bot-info">AI 实训导师 · 任务下发</span>
                <div class="bot-prompt task-brief">
                  <div class="brief-title">📋 任务目标</div>
                  <div class="brief-body">{{ selectedTask.text }}</div>
                  <div v-if="selectedTask.desc" class="brief-title" style="margin-top:8px">📝 任务要求</div>
                  <div v-if="selectedTask.desc" class="brief-body">{{ selectedTask.desc }}</div>
                </div>
              </div>
            </div>

            <!-- 对话历史 -->
            <div v-for="(msg, idx) in chatHistory" :key="idx" :class="msg.role === 'user' ? 'user-msg-wrapper' : 'bot-msg-wrapper'">
              <div v-if="msg.role === 'assistant'" class="bot-avatar-mini"><el-icon><MagicStick /></el-icon></div>
              <div :class="msg.role === 'user' ? 'user-content' : 'bot-content'">
                <span class="bot-info" v-if="msg.role === 'assistant'">AI 实训导师</span>
                <span class="bot-info" v-else>我</span>
                <div :class="msg.role === 'user' ? 'user-prompt' : 'bot-prompt'">{{ msg.content }}</div>
              </div>
            </div>

            <!-- 加载指示器 -->
            <div v-if="isCoachingLoading" class="bot-msg-wrapper">
              <div class="bot-avatar-mini"><el-icon><MagicStick /></el-icon></div>
              <div class="bot-content">
                <span class="bot-info">AI 实训导师</span>
                <div class="bot-prompt typing-indicator">
                  <span class="dot"></span><span class="dot"></span><span class="dot"></span>
                </div>
              </div>
            </div>
          </div>

          <div class="chat-input-area">
            <el-input
              v-model="chatInputValue"
              type="textarea"
              :autosize="{ minRows: 1, maxRows: 4 }"
              :placeholder="selectedTask && selectedTask.status === 'completed' ? '任务已完成，仍可继续向导师提问' : '完成任务的思考过程，有不懂的地方随时向导师提问，完成后可提交答案'"
              resize="none"
              @keydown.enter.exact.prevent="sendChatMessage"
            />
            <div class="input-btns">
              <el-button
                class="submit-btn"
                type="success"
                plain
                :disabled="!chatInputValue.trim() || isCoachingLoading"
                @click="submitAnswer"
              >
                <el-icon><CircleCheck /></el-icon>
                提交答案
              </el-button>
              <el-button
                type="primary"
                :disabled="!chatInputValue.trim() || isCoachingLoading"
                :loading="isCoachingLoading"
                @click="sendChatMessage"
              >
                <el-icon><Promotion /></el-icon>
                发送
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 未选择任务时的聊天区占位 -->
      <div v-else class="chat-section glass-card chat-placeholder">
        <div class="placeholder-body">
          <el-icon class="placeholder-icon"><MagicStick /></el-icon>
          <p>点击上方任务卡片，进入该任务的 AI 实训导师</p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { MagicStick, Aim, List, CircleCheck, Promotion, Timer, StarFilled } from '@element-plus/icons-vue'
import { learningPlanApi } from '@/api/learningPlan'
import { matchingApi } from '@/api/matching'
import { currentRadarData, matchVersion } from './profileState.js'

const CACHE_KEY = 'growth_tracker_cache'

const generateCacheKey = (profileData, jobTitle) => {
  const profileHash = JSON.stringify(profileData || [])
  return `${profileHash}_${jobTitle || 'none'}`
}

const loadFromCache = () => {
  try {
    const raw = sessionStorage.getItem(CACHE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

const saveToCache = (cacheKey, data) => {
  try {
    sessionStorage.setItem(CACHE_KEY, JSON.stringify({ cacheKey, ...data, matchVersion: matchVersion.value, timestamp: Date.now() }))
  } catch { /* quota exceeded */ }
}

const targetPosition = ref('')
const currentPhaseIndex = ref(0)
const pathSteps = ref([])
const todoList = ref([])
const pageLoading = ref(true)
const selectedTask = ref(null)
const chatInputValue = ref('')
const isCoachingLoading = ref(false)
const chatHistory = ref([])
const chatMessagesRef = ref(null)
const hasMatchData = ref(false)

const totalCount = computed(() => todoList.value.length)
const completedCount = computed(() => todoList.value.filter(t => t.status === 'completed').length)
const progressPercentage = computed(() => totalCount.value === 0 ? 0 : Math.round(completedCount.value / totalCount.value * 100))

const currentGoal = computed(() => {
  const phase = pathSteps.value[currentPhaseIndex.value]
  if (phase?.goals?.length) return phase.goals.join('；')
  if (phase?.phase_name) return phase.phase_name
  if (targetPosition.value) return `提升「${targetPosition.value}」核心能力`
  return '完成本周实训任务，稳步提升岗位能力'
})

const encouragement = computed(() => {
  if (totalCount.value === 0) return '锁定目标岗位后，我将为你生成本周实训任务'
  if (completedCount.value === 0) return '千里之行始于足下，点击下方任务卡片，开始攻克第一个任务吧！'
  if (completedCount.value === totalCount.value) return '太棒了！你已完成本周全部任务，下一阶段能力模型即将解锁，继续保持！'
  return `恭喜！你已完成 ${completedCount.value}/${totalCount.value} 个任务，比预计进度提前了，继续保持这个节奏！`
})

const statusIcon = (status) => {
  if (status === 'completed') return '✅'
  if (status === 'in_progress') return '🟡'
  return '🔵'
}

const statusLabel = (status) => {
  if (status === 'completed') return '已完成'
  if (status === 'in_progress') return '进行中'
  return '待开始'
}

const normalizeTasks = (tasks) => {
  return tasks.map((t, i) => ({
    id: t.id || i + 1,
    text: t.content || t.title || t.task || `任务 ${i + 1}`,
    desc: t.description || t.desc || '',
    time: t.estimated_time || t.time || t.duration || '30',
    difficulty: t.difficulty || t.type || '中等',
    status: t.status || 'pending',  // 保留后端真实状态
  }))
}

const isCacheValid = (cacheKey) => {
  const cached = loadFromCache()
  if (!cached || !cached.cacheKey || !cached.todoList?.length) return false
  // 5分钟内的缓存直接用，不重拉
  if (Date.now() - cached.timestamp < 5 * 60 * 1000) return true
  return cached.cacheKey === cacheKey && cached.matchVersion === matchVersion.value
}

const restoreFromCache = () => {
  const cached = loadFromCache()
  if (!cached) return false
  if (cached.targetPosition) targetPosition.value = cached.targetPosition
  if (cached.pathSteps) {
    pathSteps.value = cached.pathSteps
  }
  if (cached.todoList) todoList.value = cached.todoList
  return true
}

const fetchAllDataAndCache = async (cacheKey, forceRefresh = false) => {
  try {
    await fetchLearningPlan(forceRefresh)
    await fetchDailyTasks()
    saveToCache(cacheKey, {
      targetPosition: targetPosition.value,
      pathSteps: pathSteps.value,
      todoList: todoList.value,
    })
  } catch (err) {
    console.error('[GrowthTracker] fetchAllDataAndCache error:', err)
  } finally {
    pageLoading.value = false
  }
}

const fetchLearningPlan = async (forceRefresh = false) => {
  try {
    const { data } = await learningPlanApi.generate({ plan_type: '长期', force_refresh: forceRefresh })
    if (data.learning_plan) {
      const plan = data.learning_plan
      if (plan.target_job) targetPosition.value = plan.target_job
      if (plan.error) return
      if (plan.phases && plan.phases.length > 0) {
        pathSteps.value = plan.phases.map((p) => ({
          phase_name: p.phase_name || p.title || '',
          goals: p.goals || [],
          content: p.content || [],
          duration: p.duration || '',
        }))
        currentPhaseIndex.value = 0
      }
    }
  } catch (err) {
    console.error('[GrowthTracker] fetchLearningPlan error:', err)
  }
}

const fetchDailyTasks = async () => {
  try {
    const { data } = await learningPlanApi.dailyTasks({ phase_index: 0, _t: Date.now() })
    const expectedJob = targetPosition.value || ''
    const returnedJob = data.target_job || ''
    const needRetry = (expectedJob && returnedJob && expectedJob !== returnedJob)
      || (!data.daily_tasks || data.daily_tasks.length === 0)
    if (needRetry) {
      const { data: retry } = await learningPlanApi.dailyTasks({ phase_index: 0, _t: Date.now() })
      if (retry.daily_tasks && retry.daily_tasks.length > 0) {
        todoList.value = normalizeTasks(retry.daily_tasks)
        return
      }
      return
    }
    todoList.value = normalizeTasks(data.daily_tasks)
  } catch (err) {
    console.error('[GrowthTracker] fetchDailyTasks error:', err)
  }
}

const selectTask = (task) => {
  selectedTask.value = task
  if (task.status === 'pending') {
    task.status = 'in_progress'
    // 同步到 MySQL，刷新不丢
    syncTaskStatus(task, 'in_progress')
  }
  chatHistory.value = []
  nextTick(() => scrollChatToBottom())
  autoIntroduceTask(task)
}

const syncTaskStatus = async (task, status) => {
  try {
    if (task.id && typeof task.id === 'number') {
      await learningPlanApi.updateTask(task.id, { status })
    }
  } catch (err) {
    console.error('[GrowthTracker] sync task status failed:', err)
  }
}

const completeTask = async (task) => {
  // 先乐观更新前端
  task.status = 'completed'
  // 同步到 MySQL，刷新不丢
  try {
    if (task.id && typeof task.id === 'number') {
      await learningPlanApi.completeTask(task.id)
    }
  } catch (err) {
    console.error('[GrowthTracker] completeTask sync failed:', err)
  }
}

const autoIntroduceTask = async (task) => {
  if (isCoachingLoading.value) return
  isCoachingLoading.value = true
  try {
    const resp = await learningPlanApi.coach(
      `请以「${task.text}」任务导师的身份，向我简要说明完成这个任务需要掌握哪些关键点、推荐的学习方法，并询问我当前准备如何开始。`,
      [],
      { task_context: `任务：${task.text}；要求：${task.desc || '无'}` }
    )
    const reply = resp.data?.reply
    if (reply) chatHistory.value.push({ role: 'assistant', content: reply })
  } catch (err) {
    console.error('[GrowthTracker] autoIntroduceTask error:', err)
    chatHistory.value.push({ role: 'assistant', content: '我是你这次任务的 AI 实训导师。请描述你对任务的理解，或直接告诉我你的问题，我会一步步引导你完成。' })
  } finally {
    isCoachingLoading.value = false
    scrollChatToBottom()
  }
}

const sendChatMessage = async () => {
  const text = chatInputValue.value.trim()
  if (!text || isCoachingLoading.value) return
  chatHistory.value.push({ role: 'user', content: text })
  chatInputValue.value = ''
  isCoachingLoading.value = true
  scrollChatToBottom()
  try {
    const task = selectedTask.value
    const resp = await learningPlanApi.coach(
      text,
      chatHistory.value.slice(0, -1),
      { task_context: task ? `任务：${task.text}；要求：${task.desc || '无'}` : '' }
    )
    chatHistory.value.push({ role: 'assistant', content: resp.data?.reply || '抱歉，暂时无法回复。' })
  } catch (err) {
    console.error('[GrowthTracker] sendChatMessage error:', err)
    chatHistory.value.push({ role: 'assistant', content: '抱歉，AI 实训导师暂时不可用，请稍后再试。' })
  } finally {
    isCoachingLoading.value = false
    scrollChatToBottom()
  }
}

const submitAnswer = async () => {
  const text = chatInputValue.value.trim()
  if (!text || isCoachingLoading.value) return
  chatHistory.value.push({ role: 'user', content: `【提交答案】${text}` })
  chatInputValue.value = ''
  isCoachingLoading.value = true
  scrollChatToBottom()
  try {
    const task = selectedTask.value
    const resp = await learningPlanApi.coach(
      `这是我提交的任务「${task.text}」的答案：${text}。请评估我的掌握程度，指出不足并给出下一步改进建议。`,
      chatHistory.value.slice(0, -1),
      { task_context: `任务：${task.text}；要求：${task.desc || '无'}；这是用户的最终提交，请作为导师评估`, submission: true }
    )
    chatHistory.value.push({ role: 'assistant', content: resp.data?.reply || '已收到你的答案，正在评估...' })
    // 提交答案成功 → 任务标记为已完成
    await completeTask(task)
  } catch (err) {
    console.error('[GrowthTracker] submitAnswer error:', err)
    chatHistory.value.push({ role: 'assistant', content: '抱歉，提交失败，请稍后再试。' })
  } finally {
    isCoachingLoading.value = false
    scrollChatToBottom()
  }
}

const scrollChatToBottom = () => {
  nextTick(() => {
    const el = chatMessagesRef.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

onMounted(async () => {
  try {
    const { data } = await matchingApi.getSelectedJob()
    if (data && data.success && data.data) {
      hasMatchData.value = true
      targetPosition.value = data.data.job_title || data.data.job_name || ''
    }
  } catch { /* ignore */ }

  if (!hasMatchData.value) {
    pageLoading.value = false
    return
  }

  // 用锁定的岗位名做 key（而非空字符串）
  const cacheKey = generateCacheKey(currentRadarData.value, targetPosition.value)
  if (isCacheValid(cacheKey)) {
    restoreFromCache()
    pageLoading.value = false
    return
  }

  // 后端有缓存直接走，不传 force_refresh
  await fetchAllDataAndCache(cacheKey, false)
})

watch(matchVersion, async () => {
  sessionStorage.removeItem(CACHE_KEY)
  pathSteps.value = []
  todoList.value = []
  targetPosition.value = ''
  selectedTask.value = null
  chatHistory.value = []
  pageLoading.value = true

  if (!hasMatchData.value) {
    pageLoading.value = false
    return
  }

  const cacheKey = generateCacheKey(currentRadarData.value, targetPosition.value)
  await fetchAllDataAndCache(cacheKey, false)
})

watch(currentRadarData, (newVal, oldVal) => {
  if (!newVal || !oldVal) return
  if (JSON.stringify(newVal) !== JSON.stringify(oldVal)) {
    sessionStorage.removeItem(CACHE_KEY)
  }
})
</script>

<style scoped>
.growth-tracking-center {
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
  margin-bottom: 20px;
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.2);
}
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1e293b;
  font-size: 15px;
}
.section-title .el-icon { color: #667eea; }
.section-subtitle { font-size: 12px; color: #94a3b8; }

/* ========== 区域一：进度区 ========== */
.progress-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 24px 28px;
  background: linear-gradient(135deg, rgba(255,255,255,0.55), rgba(240,248,255,0.35));
}
.progress-left { flex: 1; min-width: 0; }
.goal-block {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 14px;
}
.goal-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #667eea;
  font-weight: 600;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 20px;
  padding: 4px 12px;
  flex-shrink: 0;
}
.goal-label .el-icon { font-size: 14px; }
.goal-text {
  font-size: 17px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.5;
  word-break: break-word;
}
.encouragement {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #64748b;
  line-height: 1.6;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  padding: 10px 14px;
}
.enc-icon { color: #f59e0b; font-size: 16px; flex-shrink: 0; }
.progress-right {
  position: relative;
  flex-shrink: 0;
  width: 88px;
  height: 88px;
}
.progress-num {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -55%);
  font-size: 18px;
  color: #1e293b;
  text-align: center;
}
.progress-num strong { font-weight: 800; }
.progress-num .total { font-size: 12px; color: #94a3b8; }
.progress-label {
  position: absolute;
  bottom: -22px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 11px;
  color: #94a3b8;
  white-space: nowrap;
}

/* ========== 区域二：任务列表 ========== */
.task-cards-horizontal {
  display: flex;
  gap: 14px;
  padding: 20px;
  overflow-x: auto;
  scrollbar-width: thin;
}
.task-card {
  flex: 0 0 200px;
  background: rgba(255, 255, 255, 0.55);
  border: 1.5px solid rgba(226, 232, 240, 0.7);
  border-radius: 14px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.task-card:hover {
  transform: translateY(-3px);
  border-color: rgba(102, 126, 234, 0.45);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.12);
}
.task-card.is-active {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08), rgba(255, 255, 255, 0.7));
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.15);
}
.task-card.is-completed {
  opacity: 0.75;
  border-color: rgba(16, 185, 129, 0.4);
}
.task-card.is-completed .task-name { text-decoration: line-through; color: #94a3b8; }
.task-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.task-number {
  font-size: 20px;
  font-weight: 800;
  color: #667eea;
  opacity: 0.7;
  font-style: italic;
}
.task-status { font-size: 11px; padding: 2px 8px; border-radius: 20px; }
.task-status.st-pending { background: rgba(96, 165, 250, 0.1); color: #3b82f6; }
.task-status.st-in_progress { background: rgba(245, 158, 11, 0.12); color: #f59e0b; }
.task-status.st-completed { background: rgba(16, 185, 129, 0.12); color: #10b981; }
.task-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 40px;
}
.task-desc {
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}
.task-meta {
  display: flex;
  gap: 10px;
  border-top: 1px dashed rgba(226, 232, 240, 0.8);
  padding-top: 8px;
}
.meta-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #94a3b8;
}
.meta-tag .el-icon { color: #667eea; font-size: 12px; }

/* ========== 区域三：聊天区 ========== */
.chat-area {
  display: flex;
  flex-direction: column;
  height: 420px;
}
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #fcfcfd;
}
.bot-msg-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 14px;
}
.bot-avatar-mini {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #70a1ff, #4a8cff);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}
.bot-content { max-width: 82%; }
.bot-info { font-size: 12px; color: #94a3b8; margin-bottom: 4px; display: block; }
.bot-prompt {
  background: white;
  padding: 12px 16px;
  border-radius: 4px 16px 16px 16px;
  color: #334155;
  font-size: 14px;
  line-height: 1.6;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
  border: 1px solid #f1f5f9;
}
.task-brief {
  background: linear-gradient(135deg, #f0f7ff, #ffffff);
  border: 1px solid rgba(102, 126, 234, 0.15);
}
.brief-title { font-weight: 700; color: #667eea; font-size: 13px; }
.brief-body { color: #334155; margin-top: 2px; }
.user-msg-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 14px;
}
.user-content { max-width: 82%; }
.user-content .bot-info { font-size: 11px; color: #94a3b8; margin-bottom: 4px; display: block; text-align: right; }
.user-prompt {
  background: linear-gradient(135deg, #70a1ff 0%, #4a8cff 100%);
  color: #ffffff;
  padding: 12px 16px;
  border-radius: 16px 4px 16px 16px;
  font-size: 14px;
  line-height: 1.6;
  box-shadow: 0 2px 12px rgba(112, 161, 255, 0.2);
  white-space: pre-wrap;
}
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 14px 20px !important;
}
.typing-indicator .dot {
  width: 7px;
  height: 7px;
  background: #94a3b8;
  border-radius: 50%;
  animation: typingBounce 1.4s ease-in-out infinite;
}
.typing-indicator .dot:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator .dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes typingBounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}
.chat-input-area {
  padding: 16px 20px;
  border-top: 1px solid #eef2f6;
  background: #ffffff;
}
.chat-input-area :deep(.el-textarea__inner) {
  border-radius: 12px;
  border: 1px solid #eef2f6;
  box-shadow: none;
  padding: 10px 12px;
  font-size: 14px;
  color: #334155;
  resize: none;
}
.chat-input-area :deep(.el-textarea__inner::placeholder) { color: #cbd5e1; }
.chat-input-area :deep(.el-textarea__inner:focus) { border-color: #70a1ff; box-shadow: 0 0 0 2px rgba(112, 161, 255, 0.1); }
.input-btns {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}
.submit-btn { border-radius: 8px; }

.chat-placeholder .placeholder-body {
  padding: 40px 20px;
  text-align: center;
  color: #94a3b8;
  font-size: 13px;
}
.chat-placeholder .placeholder-icon {
  font-size: 40px;
  color: #c7d5f5;
  margin-bottom: 10px;
}
.chat-placeholder p { margin: 0; }

.loading-state, .empty-state {
  padding: 60px 20px;
  text-align: center;
  color: #94a3b8;
  font-size: 14px;
}

@media (max-width: 768px) {
  .progress-section {
    flex-direction: column;
    align-items: flex-start;
  }
  .progress-right { align-self: center; margin-top: 10px; }
  .task-card { flex: 0 0 160px; }
  .chat-area { height: 360px; }
}
</style>