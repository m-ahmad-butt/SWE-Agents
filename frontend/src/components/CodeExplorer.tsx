import { useEffect, useState } from 'react'
import { listCodeFiles, readCodeFile } from '../api/client'

interface Props {
  projectId: string
  files: string[]
  phase: string
}

export default function CodeExplorer({ projectId, files, phase }: Props) {
  const [tree, setTree] = useState<string[]>(files)
  const [selected, setSelected] = useState<string | null>(null)
  const [content, setContent] = useState('')

  useEffect(() => {
    setTree(files)
  }, [files])

  useEffect(() => {
    if (phase === 'milestone_coding') {
      const interval = window.setInterval(() => {
        listCodeFiles(projectId).then(setTree).catch(() => {})
      }, 2000)
      return () => window.clearInterval(interval)
    }
  }, [projectId, phase])

  const openFile = async (path: string) => {
    setSelected(path)
    try {
      const text = await readCodeFile(projectId, path)
      setContent(text)
    } catch {
      setContent('Unable to load file.')
    }
  }

  if (!tree.length && phase !== 'milestone_coding') return null

  return (
    <div className="flex flex-col h-full min-h-0">
      <div className="px-3 py-2 border-b border-[#1e1e1e] flex justify-between flex-shrink-0">
        <span className="text-[11px] font-medium text-[#888] uppercase tracking-wider">Code</span>
        <span className="text-[10px] text-[#555]">{tree.length} files</span>
      </div>
      <div className="flex flex-1 min-h-0">
        <div className="w-2/5 border-r border-[#1e1e1e] overflow-y-auto p-1.5">
          {tree.length === 0 ? (
            <p className="text-[10px] text-[#444] p-2">Generating...</p>
          ) : (
            tree.map((f) => (
              <button
                key={f}
                type="button"
                onClick={() => openFile(f)}
                className={`block w-full text-left px-2 py-1 rounded text-[10px] truncate ${
                  selected === f
                    ? 'bg-[#1a1a1a] text-[#ccc] border border-[#333]'
                    : 'text-[#666] hover:text-[#999] hover:bg-[#111]'
                }`}
              >
                {f}
              </button>
            ))
          )}
        </div>
        <pre className="flex-1 overflow-auto p-2 text-[10px] text-[#777] font-mono whitespace-pre-wrap leading-relaxed">
          {selected ? content : 'Select a file'}
        </pre>
      </div>
    </div>
  )
}
