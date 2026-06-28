import { useEffect, useRef, useState } from 'react'
import type { ChatMessage } from '../api/client'

interface Props {
  messages: ChatMessage[]
  onSend: (msg: string) => void
  loading: boolean
  disabled: boolean
  waitingHint?: boolean
  projectTitle?: string
}

function agentLabel(agent: string) {
  return agent.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

export default function ChatPanel({
  messages,
  onSend,
  loading,
  disabled,
  waitingHint,
  projectTitle,
}: Props) {
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading || disabled) return
    onSend(input.trim())
    setInput('')
  }

  return (
    <div className="flex flex-col h-full min-h-0 w-full bg-[#0a0a0a]">
      <div className="px-5 py-3 border-b border-[#1e1e1e] flex-shrink-0">
        <h2 className="text-[13px] font-medium text-[#cccccc]">Chat</h2>
        {projectTitle && (
          <p className="text-[11px] text-[#6b6b6b] mt-0.5 truncate">{projectTitle}</p>
        )}
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-5 min-h-0">
        {messages.map((m, i) => (
          <div key={i} className="space-y-1.5">
            {m.role === 'assistant' && m.agent && (
              <div className="text-[11px] text-[#6b6b6b] font-medium">
                {agentLabel(m.agent)}
              </div>
            )}
            <div
              className={`text-[13px] leading-[1.6] whitespace-pre-wrap break-words ${
                m.role === 'user' ? 'text-[#e8e8e8]' : 'text-[#aaaaaa]'
              }`}
            >
              {m.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-[12px] text-[#6b6b6b]">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-white/60 animate-pulse" />
            {disabled ? 'Agents are working — this may take a minute...' : 'Agent is thinking...'}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form
        onSubmit={submit}
        className="flex-shrink-0 p-4 border-t border-[#1e1e1e]"
      >
        <div className="rounded-xl border border-[#2a2a2a] bg-[#141414] focus-within:border-[#444] transition-colors">
          <textarea
            rows={2}
            className="w-full bg-transparent px-4 py-3 text-[13px] text-[#cccccc] placeholder-[#555] focus:outline-none disabled:opacity-40 resize-none"
            placeholder={
              waitingHint && disabled
                ? 'Agents working… type "continue" to retry if stuck'
                : disabled
                  ? 'Please wait...'
                  : 'Message the team...'
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={disabled || loading}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                submit(e)
              }
            }}
          />
          <div className="flex justify-end px-3 pb-3">
            <button
              type="submit"
              disabled={disabled || loading || !input.trim()}
              className="text-[12px] px-4 py-1.5 rounded-lg bg-[#2a2a2a] hover:bg-[#333] text-[#ccc] disabled:opacity-30 transition-colors"
            >
              Send
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}
