import { useCallback, useEffect, useRef, useState } from 'react'
import {
  advanceProject,
  createProject,
  getProject,
  loadStoredProjectId,
  saveProjectId,
  sendMessage,
  type Project,
} from '../api/client'

const POLL_PHASES = new Set([
  'planning',
  'srs_generation',
  'milestone_planning',
  'milestone_coding',
  'milestone_documentation',
  'negotiation',
])

const AUTO_ADVANCE_PHASES = new Set([
  'planning',
  'srs_generation',
  'milestone_planning',
  'milestone_coding',
  'milestone_documentation',
])

export function useProject() {
  const [project, setProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(false)
  const [restoring, setRestoring] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const pollRef = useRef<number | null>(null)
  const advancingRef = useRef(false)

  const refresh = useCallback(async (id: string) => {
    const p = await getProject(id)
    setProject(p)
    saveProjectId(id)
    return p
  }, [])

  const resumeProject = useCallback(async (id: string) => {
    setLoading(true)
    setError(null)
    try {
      const p = await getProject(id)
      setProject(p)
      saveProjectId(id)
      return p
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error')
      throw e
    } finally {
      setLoading(false)
    }
  }, [])

  const goHome = useCallback(() => {
    setProject(null)
    setError(null)
  }, [])

  useEffect(() => {
    const storedId = loadStoredProjectId()
    if (!storedId) {
      setRestoring(false)
      return
    }
    getProject(storedId)
      .then((p) => {
        setProject(p)
        saveProjectId(p.id)
      })
      .catch(() => {})
      .finally(() => setRestoring(false))
  }, [])

  const startProject = useCallback(async (query: string) => {
    setLoading(true)
    setError(null)
    try {
      const p = await createProject(query)
      setProject(p)
      return p
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error')
      throw e
    } finally {
      setLoading(false)
    }
  }, [])

  const postMessage = useCallback(
    async (message: string) => {
      if (!project) return
      setLoading(true)
      setError(null)
      try {
        const p = await sendMessage(project.id, message)
        setProject(p)
        return p
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Error')
        throw e
      } finally {
        setLoading(false)
      }
    },
    [project],
  )

  useEffect(() => {
    if (!project) return
    if (!POLL_PHASES.has(project.phase)) {
      if (pollRef.current) window.clearInterval(pollRef.current)
      return
    }
    pollRef.current = window.setInterval(() => {
      refresh(project.id).catch(() => {})
    }, 1500)
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current)
    }
  }, [project?.id, project?.phase, refresh])

  useEffect(() => {
    if (!project || loading || advancingRef.current) return
    if (!AUTO_ADVANCE_PHASES.has(project.phase)) return

    advancingRef.current = true
    advanceProject(project.id)
      .then((p) => setProject(p))
      .catch(() => {})
      .finally(() => {
        advancingRef.current = false
      })
  }, [project?.id, project?.phase, project?.active_agent, project?.updated_at, loading])

  return {
    project,
    loading,
    restoring,
    error,
    startProject,
    resumeProject,
    goHome,
    postMessage,
    refresh,
  }
}
