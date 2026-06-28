import { useEffect, useRef, useState } from 'react'

export const AGENTS = [
  { id: 'requirement_engineer', label: 'Requirement Engineer', role: 'Gathers client requirements' },
  { id: 'planning_analyst', label: 'Planning Analyst', role: 'Estimates time, cost & effort' },
  { id: 'negotiation_agent', label: 'Negotiation Agent', role: 'Negotiates budget & timeline' },
  { id: 'srs_generator', label: 'SRS Generator', role: 'Creates requirements specification' },
  { id: 'project_manager', label: 'Project Manager', role: 'Splits work into milestones' },
  { id: 'backend_engineer', label: 'Backend Engineer', role: 'Generates FastAPI code' },
  { id: 'frontend_engineer', label: 'Frontend Engineer', role: 'Generates React code' },
  { id: 'documentation_agent', label: 'Documentation Agent', role: 'Writes milestone docs' },
  { id: 'customer_review', label: 'Customer Review', role: 'Approves or requests changes' },
]

interface Props {
  activeAgent: string
  phase: string
  statusMessage: string
}

function agentIndex(id: string) {
  return AGENTS.findIndex((a) => a.id === id)
}

function getAgentStatus(
  agentId: string,
  activeAgent: string,
  phase: string,
): 'active' | 'done' | 'pending' {
  if (phase === 'completed') return 'done'

  const idx = agentIndex(agentId)
  const activeIdx = agentIndex(activeAgent)

  if (agentId === activeAgent) return 'active'

  if (phase === 'milestone_coding' && agentId === 'backend_engineer' && activeAgent === 'frontend_engineer') {
    return 'done'
  }

  if (
    (phase === 'milestone_documentation' || phase === 'milestone_review') &&
    (agentId === 'backend_engineer' || agentId === 'frontend_engineer')
  ) {
    return 'done'
  }

  if (phase === 'milestone_review' && agentId === 'documentation_agent') {
    return 'done'
  }

  if (idx >= 0 && activeIdx >= 0 && idx < activeIdx) return 'done'

  return 'pending'
}

export default function AgentPipeline({ activeAgent, phase, statusMessage }: Props) {
  const isComplete = phase === 'completed'
  const activeIdx = isComplete ? AGENTS.length : agentIndex(activeAgent)
  const prevIdxRef = useRef(activeIdx)
  const [beamFrom, setBeamFrom] = useState<number | null>(null)
  const [beamTo, setBeamTo] = useState<number | null>(null)

  useEffect(() => {
    const prev = prevIdxRef.current
    if (activeIdx !== prev && activeIdx >= 0 && prev >= 0) {
      setBeamFrom(prev)
      setBeamTo(activeIdx)
      const t = window.setTimeout(() => {
        setBeamFrom(null)
        setBeamTo(null)
      }, 900)
      prevIdxRef.current = activeIdx
      return () => window.clearTimeout(t)
    }
    prevIdxRef.current = activeIdx
  }, [activeIdx])

  return (
    <div className="flex flex-col h-full min-h-0">
      <div className="flex-shrink-0 px-6 py-4 border-b border-[#1e1e1e]">
        <h2 className="text-[13px] font-medium text-[#cccccc] tracking-wide">Agent Pipeline</h2>
        <p className="text-[11px] text-[#6b6b6b] mt-1">{statusMessage}</p>
        {isComplete && (
          <div className="mt-3 rounded-lg border border-[#4ade80]/30 bg-[#4ade80]/5 px-3 py-2">
            <p className="text-[12px] font-medium text-[#4ade80]">Project Complete</p>
            <p className="text-[11px] text-[#888] mt-0.5">
              Download the ZIP and follow README.md to run your application.
            </p>
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto min-h-0 flex items-start justify-center">
        <div className="w-full max-w-2xl px-6 py-4">
          <div className="relative w-full">
            {AGENTS.map((agent, i) => {
              const status = getAgentStatus(agent.id, activeAgent, phase)
              const isActive = status === 'active'
              const isDone = status === 'done'
              const isPending = status === 'pending'
              const showBeam =
                beamFrom !== null &&
                beamTo !== null &&
                i > beamFrom &&
                i <= beamTo

              return (
                <div key={agent.id} className="relative w-full">
                  {i > 0 && (
                    <div className="relative h-5 ml-[21px]">
                      <div
                        className={`absolute left-0 top-0 bottom-0 w-px ${
                          isComplete ? 'bg-[#4ade80]/40' : 'bg-[#2a2a2a]'
                        }`}
                      />
                      {showBeam && (
                        <div className="beam-travel absolute left-[-2px] top-0 w-[5px] h-[5px] rounded-full bg-white shadow-[0_0_12px_4px_rgba(255,255,255,0.8)]" />
                      )}
                    </div>
                  )}

                  <div
                    className={`agent-card relative flex items-start gap-4 w-full rounded-xl px-4 py-3.5 transition-all duration-500 ${
                      isComplete
                        ? 'opacity-70 border border-[#4ade80]/20'
                        : isActive
                          ? 'agent-active bg-[#141414] border border-[#3a3a3a]'
                          : isDone
                            ? 'opacity-55 border border-transparent'
                            : isPending
                              ? 'opacity-35 border border-transparent'
                              : 'border border-transparent'
                    }`}
                  >
                    {isActive && !isComplete && (
                      <div className="moon-glow absolute inset-0 rounded-xl pointer-events-none" />
                    )}

                    <div
                      className={`relative z-10 flex-shrink-0 w-[10px] h-[10px] rounded-full mt-1.5 ${
                        isComplete || isDone
                          ? 'bg-[#4ade80]'
                          : isActive
                            ? 'bg-white shadow-[0_0_14px_6px_rgba(255,255,255,0.55)] moon-dot'
                            : 'bg-[#3a3a3a]'
                      }`}
                    />

                    <div className="relative z-10 flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span
                          className={`text-[14px] font-medium ${
                            isComplete || isDone
                              ? 'text-[#888]'
                              : isActive
                                ? 'text-white'
                                : 'text-[#555]'
                          }`}
                        >
                          {agent.label}
                        </span>
                        {isActive && !isComplete && (
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/10 text-white/80 animate-pulse">
                            working
                          </span>
                        )}
                        {(isDone || isComplete) && (
                          <span className="text-[10px] text-[#4ade80]/70">done</span>
                        )}
                      </div>
                      <p className={`text-[12px] mt-1 ${isActive && !isComplete ? 'text-[#999]' : 'text-[#444]'}`}>
                        {agent.role}
                      </p>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
