import { useEffect, useState } from 'react'
import type { ProjectSummary } from '../api/client'
import { listProjects } from '../api/client'

interface Props {
  onSelect: (id: string) => void
  currentId?: string | null
}

function formatDate(iso: string) {
  if (!iso) return ''
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return ''
  }
}

export default function ProjectHistory({ onSelect, currentId }: Props) {
  const [projects, setProjects] = useState<ProjectSummary[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listProjects()
      .then(setProjects)
      .catch(() => setProjects([]))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <p className="text-[12px] text-[#555] text-center py-4">Loading history...</p>
    )
  }

  if (!projects.length) {
    return (
      <p className="text-[12px] text-[#555] text-center py-4">
        No previous projects. Start a new one above.
      </p>
    )
  }

  return (
    <div className="space-y-2">
      <h2 className="text-[11px] font-medium text-[#888] uppercase tracking-wider px-1">
        Continue where you left off
      </h2>
      <ul className="space-y-1.5 max-h-[280px] overflow-y-auto">
        {projects.map((p) => (
          <li key={p.id}>
            <button
              type="button"
              onClick={() => onSelect(p.id)}
              className={`w-full text-left rounded-lg px-3 py-2.5 border transition-colors ${
                currentId === p.id
                  ? 'border-[#444] bg-[#1a1a1a]'
                  : 'border-[#2a2a2a] bg-[#111] hover:border-[#444] hover:bg-[#141414]'
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <span className="text-[13px] text-[#ccc] font-medium truncate">
                  {p.title}
                </span>
                <span className="text-[10px] text-[#555] flex-shrink-0">
                  {formatDate(p.updated_at)}
                </span>
              </div>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#1a1a1a] text-[#777] capitalize">
                  {p.phase.replace(/_/g, ' ')}
                </span>
                <span className="text-[10px] text-[#555] truncate">
                  {p.status_message}
                </span>
              </div>
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
