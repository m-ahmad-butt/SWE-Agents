import { useState } from 'react'
import AgentPipeline from './AgentPipeline'
import FilesAndDocs from './FilesAndDocs'
import type { Milestone } from '../api/client'
import { codeZipDownloadUrl, downloadFile, pdfDownloadUrl, runGuideDownloadUrl } from '../api/client'

type LeftTab = 'pipeline' | 'files'

interface Props {
  activeAgent: string
  phase: string
  statusMessage: string
  projectId: string
  srsMarkdown: string
  milestones: Milestone[]
  generatedFiles: string[]
  runGuideMarkdown?: string
}

export default function WorkspacePanel({
  activeAgent,
  phase,
  statusMessage,
  projectId,
  srsMarkdown,
  milestones,
  generatedFiles,
  runGuideMarkdown,
}: Props) {
  const [tab, setTab] = useState<LeftTab>('pipeline')

  const handlePdf = async () => {
    try {
      await downloadFile(pdfDownloadUrl(projectId), `project_${projectId}_srs.pdf`)
    } catch (e) {
      alert(e instanceof Error ? e.message : 'PDF not available yet')
    }
  }

  const handleZip = async () => {
    try {
      await downloadFile(codeZipDownloadUrl(projectId), `project_${projectId}_code.zip`)
    } catch (e) {
      alert(e instanceof Error ? e.message : 'No generated code yet')
    }
  }

  const handleReadme = async () => {
    try {
      await downloadFile(runGuideDownloadUrl(projectId), `README_${projectId}.md`)
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Run guide not available yet')
    }
  }

  return (
    <div className="flex flex-col h-full min-h-0 bg-[#0a0a0a]">
      <div className="flex-shrink-0 flex items-center justify-between px-4 py-2 border-b border-[#1e1e1e]">
        <div className="flex gap-1">
          <button
            type="button"
            onClick={() => setTab('pipeline')}
            className={`text-[11px] px-3 py-1.5 rounded-md ${
              tab === 'pipeline'
                ? 'bg-[#1a1a1a] text-white border border-[#333]'
                : 'text-[#666] hover:text-[#aaa]'
            }`}
          >
            Agent Pipeline
          </button>
          <button
            type="button"
            onClick={() => setTab('files')}
            className={`text-[11px] px-3 py-1.5 rounded-md ${
              tab === 'files'
                ? 'bg-[#1a1a1a] text-white border border-[#333]'
                : 'text-[#666] hover:text-[#aaa]'
            }`}
          >
            Files & Docs
          </button>
        </div>
        <div className="flex gap-1.5">
          <button
            type="button"
            onClick={handlePdf}
            className="text-[10px] px-2 py-1 rounded bg-[#1a1a1a] border border-[#2a2a2a] text-[#888] hover:text-[#ccc]"
          >
            PDF
          </button>
          <button
            type="button"
            onClick={handleZip}
            className="text-[10px] px-2 py-1 rounded bg-[#1a1a1a] border border-[#2a2a2a] text-[#888] hover:text-[#ccc]"
          >
            ZIP
          </button>
          {phase === 'completed' && (
            <button
              type="button"
              onClick={handleReadme}
              className="text-[10px] px-2 py-1 rounded bg-[#4ade80]/10 border border-[#4ade80]/30 text-[#4ade80] hover:bg-[#4ade80]/20"
            >
              README
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 min-h-0 overflow-hidden">
        {tab === 'pipeline' ? (
          <AgentPipeline
            activeAgent={activeAgent}
            phase={phase}
            statusMessage={statusMessage}
          />
        ) : (
          <FilesAndDocs
            projectId={projectId}
            srsMarkdown={srsMarkdown}
            milestones={milestones}
            generatedFiles={generatedFiles}
            runGuideMarkdown={runGuideMarkdown || ''}
            phase={phase}
          />
        )}
      </div>
    </div>
  )
}
