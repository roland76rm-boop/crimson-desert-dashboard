const API_BASE = import.meta.env.VITE_API_URL || '/api'

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`)
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`)
  return res.json()
}

export interface CharacterData {
  name: string | null
  level: number | null
  playtime_seconds: number | null
  currency_silver: number | null
  stats: Record<string, number>
  snapshot_id: number
  uploaded_at: string
}

export interface InventoryItem {
  item_key: string
  item_name: string | null
  stack_count: number
  slot_index: number
  category: string
}

export interface EquipmentItem {
  item_key: string
  item_name: string | null
  enchant_level: number
  endurance: number
  sharpness: number
  slot_type: string
}

export interface Quest {
  quest_key: string
  quest_name: string | null
  status: string
  completed_at: string | null
}

export interface Mercenary {
  merc_key: string
  name: string
  type: string
  custom_name: string | null
}

export interface SnapshotSummary {
  id: number
  uploaded_at: string
  save_slot: string | null
  character_name: string | null
  character_level: number | null
  playtime_seconds: number | null
  currency_silver: number | null
}

export interface TimelinePoint {
  uploaded_at: string
  character_level: number | null
  currency_silver: number | null
  playtime_seconds: number | null
  inventory_count: number
  quests_completed: number
}

export interface HealthResponse {
  status: string
  service: string
}

export const api = {
  character: () => fetchJson<CharacterData>('/character'),
  inventory: () => fetchJson<InventoryItem[]>('/inventory'),
  equipment: () => fetchJson<EquipmentItem[]>('/equipment'),
  quests: () => fetchJson<Quest[]>('/quests'),
  mercenaries: () => fetchJson<Mercenary[]>('/mercenaries'),
  snapshots: (limit = 20) => fetchJson<SnapshotSummary[]>(`/snapshots?limit=${limit}`),
  timeline: (days = 30) => fetchJson<TimelinePoint[]>(`/timeline?days=${days}`),
  health: () => fetchJson<HealthResponse>('/health'),
}
