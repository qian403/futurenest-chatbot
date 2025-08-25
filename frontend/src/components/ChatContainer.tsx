import React, { useEffect, useState } from 'react'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import { postChat, buildChatPayload, listTemplates, ingestTemplate } from '@/api/client'
import type { TemplateMeta } from '@/api/types'

type Msg = { role: 'user' | 'assistant'; content: string }

export default function ChatContainer() {
    const [messages, setMessages] = useState<Msg[]>([])
    const [loading, setLoading] = useState(false)
    const [templates, setTemplates] = useState<TemplateMeta[]>([])
    const [selected, setSelected] = useState<string>('')
    const [ingesting, setIngesting] = useState(false)

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
                setMessages((prev) => [...prev, { role: 'assistant', content: res.data.answer }])
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

    const onIngestTemplate = async () => {
        if (!selected) return
        setIngesting(true)
        try {
            const res = await ingestTemplate(selected)
            if (res.success) {
                alert(`模板匯入完成：${res.data.doc_id}（chunks=${res.data.chunks}）`)
            } else {
                alert(`匯入失敗：${res.error?.message || ''}`)
            }
        } catch (e) {
            console.error(e)
            alert('匯入時發生錯誤')
        } finally {
            setIngesting(false)
        }
    }

    const current = templates.find(t => t.template_id === selected)

    return (
        <div className="flex flex-col gap-4">
            <div className="rounded-xl border border-white/10 bg-slate-900/40 backdrop-blur-md p-3 shadow-sm">
                <div className="flex gap-2 items-end">
                    <div className="flex-1">
                        <label className="block text-sm mb-1" htmlFor="template-select">選擇預設模板</label>
                        <select id="template-select" title="選擇預設模板" className="w-full rounded-md bg-slate-800/70 border border-white/10 p-2 text-slate-100" value={selected} onChange={e => setSelected(e.target.value)}>
                            {templates.map(t => (
                                <option key={t.template_id} value={t.template_id}>{t.title}</option>
                            ))}
                        </select>
                    </div>
                    <button disabled={ingesting || !selected} onClick={onIngestTemplate} className="h-10 px-4 rounded-md bg-emerald-600/90 hover:bg-emerald-500/90 text-white disabled:opacity-50 border border-white/10">
                        {ingesting ? '匯入中…' : '匯入模板'}
                    </button>
                </div>
                {selected && (
                    <div className="mt-2 text-sm text-slate-300/90 space-y-1">
                        <p>目前模板：<span className="font-medium text-slate-100">{current?.title || selected}</span></p>
                        <p>{current?.description}</p>
                    </div>
                )}
            </div>

            <MessageList messages={messages} />
            <div className="rounded-xl border border-white/10 bg-slate-900/40 backdrop-blur-md p-3 shadow-sm">
                <MessageInput loading={loading} onSend={onSend} />
            </div>
        </div>
    )
}
