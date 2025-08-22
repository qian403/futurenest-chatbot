import React from 'react'

type Msg = { role: 'user' | 'assistant'; content: string }

export default function MessageList({ messages }: { messages: Msg[] }) {
    return (
        <div className="space-y-3 my-4">
            {messages.map((m, i) => (
                <div key={i} className={m.role === 'user' ? 'flex justify-end' : 'flex justify-start'}>
                    <div className={[
                        'px-4 py-2 rounded-2xl max-w-[75%] whitespace-pre-wrap break-words shadow',
                        m.role === 'user' ? 'bg-blue-500/20 border border-blue-300/20' : 'bg-white/10 border border-white/10',
                    ].join(' ')}>
                        {m.content}
                    </div>
                </div>
            ))}
        </div>
    )
}
