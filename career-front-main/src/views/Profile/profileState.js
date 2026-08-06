import { ref, computed } from 'vue'
import api from '@/api/client'

const DIMENSIONS = ['专业技能', '创新能力', '学习能力', '实习能力', '抗压能力', '沟通能力', '证书']

// 模块级变量 — 页面刷新后从后端恢复
export const currentRadarData = ref([0, 0, 0, 0, 0, 0, 0])
export const dimensionDetailsRaw = ref(null)

// 能力对标版本号，每次重新对标时递增，用于触发个性化实训台重新加载
export const matchVersion = ref(0)

export const dimensionDetails = computed(() => {
  if (dimensionDetailsRaw.value) return dimensionDetailsRaw.value
  return Object.fromEntries(DIMENSIONS.map(d => [d, { status: '待采集', desc: '请通过对话提供信息', type: 'info' }]))
})

// 标记是否已尝试从后端加载
let _loadedFromBackend = false

// 页面刷新后从后端 MySQL 恢复用户画像数据
export async function loadProfileFromBackend() {
  if (_loadedFromBackend) return
  _loadedFromBackend = true
  try {
    const { data } = await api.get('/resume/profile')
    if (data.data && data.data.radar_data) {
      currentRadarData.value = data.data.radar_data
      dimensionDetailsRaw.value = data.data.dimension_details || null
    }
  } catch {
    // 未登录或首次使用，忽略
  }
}

// 标记画像已更新（需要重新加载实训台等）
export function bumpMatchVersion() {
  matchVersion.value++
}
