const API = '/api'
export const PROJECT_STORAGE_KEY = 'ai_software_company_project_id'

export interface ProjectSummary {
  id: string
  title: string
  phase: string
  active_agent: string
  status_message: string
  updated_at: string
  created_at: string
}

export interface ChatMessage {
  role: string
  content: string
  agent: string
  timestamp: string
}

export interface Milestone {
  number: number
  title: string
  description: string
  backend_scope: string[]
  frontend_scope: string[]
  status: string
  documentation: string
}

export interface Project {
  id: string
  title: string
  phase: string
  active_agent: string
  status_message: string
  chat_history: ChatMessage[]
  milestones: Milestone[]
  current_milestone_index: number
  generated_files: string[]
  srs_markdown?: string
  run_guide_markdown?: string
  updated_at?: string
  estimate?: {
    timeline_months: number
    estimated_cost_usd: number
    complexity: string
  }
}

export async function listProjects(): Promise<ProjectSummary[]> {
  const res = await fetch(`${API}/projects`)
  if (!res.ok) return []
  const data = await res.json()
  return data.projects || []
}

export async function createProject(query: string): Promise<Project> {
  const res = await fetch(`${API}/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })
  if (!res.ok) throw new Error('Failed to create project')
  const project = await res.json()
  localStorage.setItem(PROJECT_STORAGE_KEY, project.id)
  return project
}

export async function getProject(id: string): Promise<Project> {
  const res = await fetch(`${API}/projects/${id}`)
  if (!res.ok) throw new Error('Failed to load project')
  return res.json()
}

export async function sendMessage(id: string, message: string): Promise<Project> {
  const res = await fetch(`${API}/projects/${id}/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  })
  if (!res.ok) throw new Error('Failed to send message')
  const project = await res.json()
  localStorage.setItem(PROJECT_STORAGE_KEY, project.id)
  return project
}

export async function advanceProject(id: string): Promise<Project> {
  const res = await fetch(`${API}/projects/${id}/advance`, { method: 'POST' })
  if (!res.ok) throw new Error('Failed to advance project')
  const project = await res.json()
  localStorage.setItem(PROJECT_STORAGE_KEY, project.id)
  return project
}

export async function listCodeFiles(id: string): Promise<string[]> {
  const res = await fetch(`${API}/projects/${id}/code`)
  if (!res.ok) return []
  const data = await res.json()
  return data.files || []
}

export async function readCodeFile(id: string, path: string): Promise<string> {
  const res = await fetch(`${API}/projects/${id}/code/${path}`)
  if (!res.ok) throw new Error('File not found')
  const data = await res.json()
  return data.content
}

export async function downloadFile(url: string, filename: string): Promise<void> {
  const res = await fetch(url)
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Download failed')
  }
  const blob = await res.blob()
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  link.click()
  URL.revokeObjectURL(link.href)
}

export function pdfDownloadUrl(id: string): string {
  return `${API}/projects/${id}/srs/pdf`
}

export function codeZipDownloadUrl(id: string): string {
  return `${API}/projects/${id}/code/download`
}

export function runGuideDownloadUrl(id: string): string {
  return `${API}/projects/${id}/run-guide/download`
}

export async function getRunGuide(id: string): Promise<string> {
  const res = await fetch(`${API}/projects/${id}/run-guide`)
  if (!res.ok) return ''
  const data = await res.json()
  return data.run_guide_markdown || ''
}

export function saveProjectId(id: string) {
  localStorage.setItem(PROJECT_STORAGE_KEY, id)
}

export function loadStoredProjectId(): string | null {
  return localStorage.getItem(PROJECT_STORAGE_KEY)
}

export function clearStoredProjectId() {
  localStorage.removeItem(PROJECT_STORAGE_KEY)
}
