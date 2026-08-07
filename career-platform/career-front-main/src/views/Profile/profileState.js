import { ref, computed } from 'vue'
import api from '@/api/client'

const DIMENSIONS = ['专业技能', '创新能力', '学习能力', '实习能力', '抗压能力', '沟通能力', '证书']

export const currentRadarData = ref([0, 0, 0, 0, 0, 0, 0])
export const dimensionDetailsRaw = ref(null)
export const matchVersion = ref(0)

export const dimensionDetails = computed(() => {
  if (dimensionDetailsRaw.value) return dimensionDetailsRaw.value
  return Object.fromEntries(DIMENSIONS.map(d => [d, { status: '待采集', desc: '请通过对话提供信息', type: 'info' }]))
})

// 页面刷新后从后端 MySQL 恢复用户画像数据
export async function loadProfileFromBackend() {
  const hasData = currentRadarData.value.some(v => v > 0)
  console.log('[Profile] 尝试从MySQL恢复... hasData=', hasData)
  if (hasData) return
  try {
    const { data } = await api.get('/resume/profile')
    console.log('[Profile] API返回:', JSON.stringify(data))
    const profile = data.data
    if (profile && profile.radar_data && profile.radar_data.some(v => v > 0)) {
      currentRadarData.value = profile.radar_data
      dimensionDetailsRaw.value = profile.dimension_details || null
      console.log('[Profile] 从MySQL恢复画像成功')
    } else {
      console.log('[Profile] MySQL中无画像数据')
    }
  } catch (err) {
    console.error('[Profile] 加载画像失败:', err)
  }
}

export function bumpMatchVersion() {
  matchVersion.value++
}
