import React, { useEffect, useRef, useState } from 'react'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import { postChat, buildChatPayload, listTemplates } from '@/api/client'
import type { TemplateMeta, ChatSource } from '@/api/types'

type Msg = { role: 'user' | 'assistant'; content: string; sources?: ChatSource[] }

export default function ChatContainer() {
    const [messages, setMessages] = useState<Msg[]>([])
    const [loading, setLoading] = useState(false)
    const [templates, setTemplates] = useState<TemplateMeta[]>([])
    const [selected, setSelected] = useState<string>('')
    const scrollEndRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        (async () => {
            const res = await listTemplates()
            if (res.success) {
                setTemplates(res.data)
                if (res.data.length > 0) setSelected(res.data[0].template_id)
            } else {
                console.warn('listTemplates error', res.error)
            }
        })()
    }, [])

    useEffect(() => {
        scrollEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
    }, [messages, loading])

    const onSend = async (text: string) => {
        if (!text.trim()) return
        setLoading(true)

        const nextHistory: Msg[] = [...messages, { role: 'user', content: text }]
        setMessages(nextHistory)
        try {
            const history = nextHistory.map((m) => ({ role: m.role, content: m.content }))
            const payload = buildChatPayload(text, history)
            const res = await postChat(payload)
            if (res.success) {
                setMessages((prev) => [...prev, { role: 'assistant', content: res.data.answer, sources: res.data.sources }])
            } else {
                console.warn('API error', res.error)
                setMessages((prev) => [
                    ...prev,
                    { role: 'assistant', content: res.error?.message || '發生錯誤，請稍後再試' },
                ])
            }
        } catch (e) {
            console.error(e)
            setMessages((prev) => [...prev, { role: 'assistant', content: '發生錯誤，請稍後再試' }])
        } finally {
            setLoading(false)
        }
    }

    const current = templates.find(t => t.template_id === selected)
    const isEmpty = messages.length === 0

    return (
        <div className="flex flex-col h-screen">
            <header className="sticky top-0 z-10 border-b border-line bg-canvas/85 backdrop-blur-sm">
                <div className="mx-auto max-w-prose px-4 h-14 flex items-center justify-between gap-4">
                    <div className="flex items-center gap-2">
                        <div className="h-6 w-6 rounded-md bg-accent/15 border border-accent/30 grid place-items-center">
                            <div className="h-1.5 w-1.5 rounded-full bg-accent" />
                        </div>
                        <span className="text-sm font-medium tracking-tight text-ink">FutureNest Chat</span>
                    </div>
                    <label className="flex items-center gap-2 text-xs">
                        <span className="text-muted">模板</span>
                        <select
                            aria-label="選擇預設模板"
                            className="rounded-md bg-surface border border-line px-2.5 py-1.5 text-xs text-ink hover:border-line/80 focus:outline-none focus:ring-1 focus:ring-accent/60 focus:border-accent/60 transition cursor-pointer"
                            value={selected}
                            onChange={e => setSelected(e.target.value)}
                        >
                            {templates.length === 0 && <option value="">載入中…</option>}
                            {templates.map(t => (
                                <option key={t.template_id} value={t.template_id}>{t.title}</option>
                            ))}
                        </select>
                    </label>
                </div>
            </header>

            <main className="flex-1 overflow-y-auto scrollbar-thin">
                <div className="mx-auto max-w-prose px-4">
                    {isEmpty ? (
                        <div className="min-h-[60vh] flex flex-col items-center justify-center text-center py-20">
                            <div className="h-12 w-12 rounded-2xl bg-accent/10 border border-accent/20 grid place-items-center mb-5">
                                <div className="h-2 w-2 rounded-full bg-accent" />
                            </div>
                            <h1 className="text-2xl font-semibold tracking-tight text-ink mb-2">
                                有什麼想問的？
                            </h1>
                            <p className="text-sm text-muted mb-6 max-w-sm">
                                FutureNest Chat — 基於 RAG 的問答助理
                            </p>
                            {current && (
                                <div className="inline-flex items-center gap-2 rounded-full bg-surface border border-line px-3 py-1.5 text-xs text-muted">
                                    <span className="h-1.5 w-1.5 rounded-full bg-accent/70" />
                                    <span>目前模板</span>
                                    <span className="text-ink">{current.title}</span>
                                </div>
                            )}
                            {current?.description && (
                                <p className="mt-3 text-xs text-muted/80 max-w-md leading-relaxed">
                                    {current.description}
                                </p>
                            )}
                        </div>
                    ) : (
                        <MessageList messages={messages} loading={loading} />
                    )}
                    <div ref={scrollEndRef} />
                </div>
            </main>

            <footer className="border-t border-line bg-canvas">
                <div className="mx-auto max-w-prose px-4 py-3">
                    <MessageInput loading={loading} onSend={onSend} />
                    <p className="mt-2 text-[11px] text-muted/70 text-center">
                        Enter 送出，Shift+Enter 換行
                        {current && !isEmpty && <span className="mx-2">·</span>}
                        {current && !isEmpty && <span>模板：{current.title}</span>}
                    </p>
                </div>
            </footer>
        </div>
    )
}
