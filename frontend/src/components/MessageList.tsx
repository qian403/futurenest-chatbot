import React from 'react'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

type Msg = { role: 'user' | 'assistant'; content: string }

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
                            <div dangerouslySetInnerHTML={renderMarkdownSafe(m.content)} />
                        ) : (
                            <div className="whitespace-pre-wrap">{m.content}</div>
                        )}
                    </div>
                </div>
            ))}
        </div>
    )
}
