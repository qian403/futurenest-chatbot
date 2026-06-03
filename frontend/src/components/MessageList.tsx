import React from 'react'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'
import type { ChatSource } from '@/api/types'

type Msg = { role: 'user' | 'assistant'; content: string; sources?: ChatSource[] }

const md = new MarkdownIt({
    html: false,
    linkify: true,
    breaks: true,
})

function renderMarkdownSafe(src: string): { __html: string } {
    const html = md.render(src)
    const clean = DOMPurify.sanitize(html, { USE_PROFILES: { html: true } })
    return { __html: clean }
}

function AssistantAvatar() {
    return (
        <div className="shrink-0 h-7 w-7 rounded-md bg-accent/15 border border-accent/30 grid place-items-center">
            <div className="h-1.5 w-1.5 rounded-full bg-accent" />
        </div>
    )
}

function Sources({ sources }: { sources: ChatSource[] }) {
    return (
        <details className="group mt-4 rounded-lg border border-line bg-surface/60">
            <summary className="cursor-pointer list-none px-3 py-2 text-xs text-muted hover:text-ink transition flex items-center gap-2 select-none">
                <svg
                    className="h-3 w-3 transition-transform group-open:rotate-90"
                    viewBox="0 0 12 12"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                >
                    <path d="M4 2.5L8 6l-4 3.5" />
                </svg>
                <span>參考資料</span>
                <span className="text-muted/60">({sources.length})</span>
            </summary>
            <div className="px-3 pb-3 pt-1 space-y-2">
                {sources.map((source, idx) => (
                    <div key={idx} className="rounded-md border border-line bg-canvas/60 px-3 py-2 text-xs">
                        {(source.article_reference || source.document_id) && (
                            <div className="text-muted mb-1">
                                <span className="text-accent/90">{source.article_reference || source.document_id}</span>
                            </div>
                        )}
                        {source.snippet && (
                            <div className="text-ink/85 leading-relaxed">
                                {source.snippet}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </details>
    )
}

function TypingIndicator() {
    return (
        <div className="flex items-start gap-3 py-6">
            <AssistantAvatar />
            <div className="flex items-center gap-1.5 pt-2">
                <span className="h-1.5 w-1.5 rounded-full bg-muted animate-pulse-dot" style={{ animationDelay: '0s' }} />
                <span className="h-1.5 w-1.5 rounded-full bg-muted animate-pulse-dot" style={{ animationDelay: '0.2s' }} />
                <span className="h-1.5 w-1.5 rounded-full bg-muted animate-pulse-dot" style={{ animationDelay: '0.4s' }} />
            </div>
        </div>
    )
}

export default function MessageList({ messages, loading = false }: { messages: Msg[]; loading?: boolean }) {
    return (
        <div className="py-6 space-y-2">
            {messages.map((m, i) => (
                m.role === 'user' ? (
                    <div key={i} className="flex justify-end py-3">
                        <div className="max-w-[85%] rounded-2xl bg-elevated border border-line px-4 py-2.5 text-[15px] leading-7 text-ink whitespace-pre-wrap break-words">
                            {m.content}
                        </div>
                    </div>
                ) : (
                    <div key={i} className="flex items-start gap-3 py-4">
                        <AssistantAvatar />
                        <div className="flex-1 min-w-0 pt-0.5">
                            <div
                                className="msg-prose text-[15px] break-words"
                                dangerouslySetInnerHTML={renderMarkdownSafe(m.content)}
                            />
                            {m.sources && m.sources.length > 0 && <Sources sources={m.sources} />}
                        </div>
                    </div>
                )
            ))}
            {loading && <TypingIndicator />}
        </div>
    )
}
