import { useState } from 'react'
import ChatPanel from './components/ChatPanel'
import ProjectHistory from './components/ProjectHistory'
import WorkspacePanel from './components/WorkspacePanel'
import { loadStoredProjectId } from './api/client'
import { useProject } from './hooks/useProject'

const INTERACTIVE = new Set(['requirements', 'negotiation', 'milestone_review', 'proposal_review'])

function App() {
  const {
    project,
    loading,
    restoring,
    error,
    startProject,
    resumeProject,
    goHome,
    postMessage,
  } = useProject()
  const [query, setQuery] = useState('')

  const handleStart = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return
    await startProject(query.trim())
  }

  const handleResume = async (id: string) => {
    await resumeProject(id)
  }

  if (restoring) {
    return (
      <div className="h-screen flex items-center justify-center bg-[#0a0a0a] text-[#666] text-sm">
        Loading project...
      </div>
    )
  }

  if (!project) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0a0a0a] p-6">
        <div className="max-w-lg w-full space-y-6">
          <div className="text-center">
            <div className="inline-flex items-center gap-2 mb-3">
              <span className="w-2 h-2 rounded-full bg-white shadow-[0_0_10px_3px_rgba(255,255,255,0.5)] moon-dot" />
              <h1 className="text-xl font-medium text-[#cccccc]">Agentic Software Company</h1>
            </div>
            <p className="text-[13px] text-[#6b6b6b]">
              Let agents cook for you!!!
            </p>
          </div>
          <form onSubmit={handleStart} className="space-y-3">
            <div className="rounded-lg border border-[#2a2a2a] bg-[#141414] focus-within:border-[#444] transition-colors">
              <textarea
                className="w-full bg-transparent p-4 text-[13px] text-[#cccccc] placeholder-[#555] min-h-[100px] focus:outline-none resize-none"
                placeholder="I want to build a hospital management web application..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </div>
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="w-full py-2.5 rounded-lg bg-[#2a2a2a] hover:bg-[#333] text-[13px] text-[#ccc] font-medium disabled:opacity-40 transition-colors"
            >
              {loading ? 'Starting...' : 'Start New Project'}
            </button>
          </form>

          <div className="border-t border-[#1e1e1e] pt-4">
            <ProjectHistory
              onSelect={handleResume}
              currentId={loadStoredProjectId()}
            />
          </div>

          {error && <p className="text-red-400/80 text-[12px] text-center">{error}</p>}
        </div>
      </div>
    )
  }

  const chatEnabled = true
  const showWaitHint = !INTERACTIVE.has(project.phase)

  return (
    <div className="h-screen flex flex-col bg-[#0a0a0a] overflow-hidden">
      <header className="flex-shrink-0 flex items-center justify-between px-4 py-2 border-b border-[#1e1e1e]">
        <div className="flex items-center gap-3 min-w-0">
          <span className="w-1.5 h-1.5 rounded-full bg-white/80 flex-shrink-0" />
          <h1 className="text-[13px] font-medium text-[#cccccc] truncate">{project.title}</h1>
          <span className="text-[11px] text-[#555] capitalize hidden sm:inline">
            {project.phase === 'completed' ? (
              <span className="text-[#4ade80]">Complete</span>
            ) : (
              project.phase.replace(/_/g, ' ')
            )}
          </span>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          {project.estimate && (
            <div className="text-[11px] text-[#6b6b6b]">
              ${project.estimate.estimated_cost_usd?.toLocaleString()} ·{' '}
              {project.estimate.timeline_months}mo
            </div>
          )}
          <button
            type="button"
            onClick={goHome}
            className="text-[10px] text-[#555] hover:text-[#aaa]"
          >
            History
          </button>
        </div>
      </header>

      <div className="flex-1 grid grid-cols-[minmax(0,7fr)_minmax(340px,3fr)] min-h-0 overflow-hidden">
        <div className="min-h-0 overflow-hidden h-full">
          <WorkspacePanel
            activeAgent={project.active_agent}
            phase={project.phase}
            statusMessage={project.status_message}
            projectId={project.id}
            srsMarkdown={project.srs_markdown || ''}
            milestones={project.milestones}
            generatedFiles={project.generated_files}
            runGuideMarkdown={project.run_guide_markdown || ''}
          />
        </div>

        <div className="min-h-0 overflow-hidden h-full border-l border-[#1e1e1e]">
          <ChatPanel
            messages={project.chat_history}
            onSend={(msg) => postMessage(msg)}
            loading={loading}
            disabled={!chatEnabled}
            waitingHint={showWaitHint}
            projectTitle={project.title}
          />
        </div>
      </div>

      {error && (
        <div className="flex-shrink-0 px-4 py-1 text-red-400/80 text-[11px] border-t border-[#1e1e1e]">
          {error}
        </div>
      )}
    </div>
  )
}

export default App
