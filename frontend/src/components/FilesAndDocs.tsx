import { useState } from 'react'
import type { Milestone } from '../api/client'
import CodeExplorer from './CodeExplorer'

type DocTab = 'srs' | 'milestones' | 'code' | 'guide'

interface Props {
  projectId: string
  srsMarkdown: string
  milestones: Milestone[]
  generatedFiles: string[]
  runGuideMarkdown: string
  phase: string
}

export default function FilesAndDocs({
  projectId,
  srsMarkdown,
  milestones,
  generatedFiles,
  runGuideMarkdown,
  phase,
}: Props) {
  const [tab, setTab] = useState<DocTab>(phase === 'completed' ? 'guide' : 'srs')
  const [selectedMilestone, setSelectedMilestone] = useState(0)

  const tabs: { id: DocTab; label: string }[] = [
    { id: 'srs', label: 'SRS' },
    { id: 'milestones', label: 'Milestones' },
    { id: 'code', label: 'Code' },
    ...(phase === 'completed' || runGuideMarkdown
      ? [{ id: 'guide' as DocTab, label: 'Run Guide' }]
      : []),
  ]

  const ms = milestones[selectedMilestone]

  return (
    <div className="flex flex-col h-full min-h-0 bg-[#0a0a0a]">
      <div className="flex-shrink-0 px-4 py-2 border-b border-[#1e1e1e] flex gap-1">
        {tabs.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`text-[11px] px-3 py-1.5 rounded-md transition-colors ${
              tab === t.id
                ? 'bg-[#1a1a1a] text-white border border-[#333]'
                : 'text-[#666] hover:text-[#aaa]'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="flex-1 min-h-0 overflow-hidden">
        {tab === 'srs' && (
          <div className="h-full overflow-y-auto p-4">
            {srsMarkdown ? (
              <pre className="text-[12px] text-[#aaa] whitespace-pre-wrap font-mono leading-relaxed">
                {srsMarkdown}
              </pre>
            ) : (
              <p className="text-[12px] text-[#555]">
                SRS will appear here after the SRS Generator runs.
              </p>
            )}
          </div>
        )}

        {tab === 'milestones' && (
          <div className="h-full flex flex-col min-h-0">
            {milestones.length === 0 ? (
              <p className="p-4 text-[12px] text-[#555]">No milestones yet.</p>
            ) : (
              <>
                <div className="flex-shrink-0 flex gap-1 p-2 border-b border-[#1e1e1e] overflow-x-auto">
                  {milestones.map((m, i) => (
                    <button
                      key={m.number}
                      type="button"
                      onClick={() => setSelectedMilestone(i)}
                      className={`text-[10px] px-2 py-1 rounded whitespace-nowrap ${
                        i === selectedMilestone
                          ? 'bg-[#1a1a1a] text-[#ccc] border border-[#333]'
                          : 'text-[#555] hover:text-[#888]'
                      }`}
                    >
                      M{m.number}: {m.title}
                    </button>
                  ))}
                </div>
                <div className="flex-1 overflow-y-auto p-4">
                  {ms?.documentation ? (
                    <pre className="text-[12px] text-[#aaa] whitespace-pre-wrap font-mono leading-relaxed">
                      {ms.documentation}
                    </pre>
                  ) : (
                    <p className="text-[12px] text-[#555]">
                      Documentation for milestone {ms?.number} not generated yet.
                    </p>
                  )}
                </div>
              </>
            )}
          </div>
        )}

        {tab === 'code' && (
          <CodeExplorer projectId={projectId} files={generatedFiles} phase={phase} />
        )}

        {tab === 'guide' && (
          <div className="h-full overflow-y-auto p-4">
            {runGuideMarkdown ? (
              <>
                <div className="mb-4 rounded-lg border border-[#4ade80]/20 bg-[#4ade80]/5 px-3 py-2">
                  <p className="text-[12px] text-[#4ade80] font-medium">How to run your project</p>
                  <p className="text-[11px] text-[#888] mt-1">
                    Download the ZIP, unzip it, and follow these instructions. README.md is also
                    included inside the ZIP.
                  </p>
                </div>
                <pre className="text-[12px] text-[#aaa] whitespace-pre-wrap font-mono leading-relaxed">
                  {runGuideMarkdown}
                </pre>
              </>
            ) : (
              <p className="text-[12px] text-[#555]">
                Run guide will appear here when the project is complete.
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
