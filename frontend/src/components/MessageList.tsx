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

export default function MessageList({ messages }: { messages: Msg[] }) {
    return (
        <div className="space-y-3 my-4">
            {messages.map((m, i) => (
                <div key={i} className={m.role === 'user' ? 'flex justify-end' : 'flex justify-start'}>
                    <div className={[
                        'px-4 py-2 rounded-2xl max-w-[75%] break-words shadow prose prose-invert prose-sm',
                        m.role === 'user' ? 'bg-blue-500/20 border border-blue-300/20' : 'bg-white/10 border border-white/10',
                    ].join(' ')}>
                        {m.role === 'assistant' ? (
                            <>
                                <div dangerouslySetInnerHTML={renderMarkdownSafe(m.content)} />
                                {m.sources && m.sources.length > 0 && (
                                    <div className="mt-3 pt-3 border-t border-white/10">
                                        <div className="text-xs text-slate-400 mb-2 font-medium">參考資料：</div>
                                        <div className="space-y-2">
                                            {m.sources.map((source, idx) => (
                                                <div key={idx} className="p-2 bg-slate-800/50 rounded-lg text-xs">
                                                    {source.document_id && (
                                                        <div className="text-slate-300 mb-1">
                                                            <span className="text-blue-300">文件ID:</span> {source.document_id}
                                                        </div>
                                                    )}
                                                    {source.snippet && (
                                                        <div className="text-slate-300 leading-relaxed">
                                                            "{source.snippet}"
                                                        </div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </>
                        ) : (
                            <div className="whitespace-pre-wrap">{m.content}</div>
                        )}
                    </div>
                </div>
            ))}
        </div>
    )
}
