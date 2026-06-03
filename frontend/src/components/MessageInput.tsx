import React, { useEffect, useRef, useState } from 'react'

type CompositionKeyboardEvent = React.KeyboardEvent<HTMLTextAreaElement> & {
    nativeEvent: KeyboardEvent & { isComposing?: boolean; keyCode?: number }
}

export default function MessageInput({ loading, onSend }: { loading: boolean; onSend: (text: string) => void }) {
    const [text, setText] = useState('')
    const [isComposing, setIsComposing] = useState(false)
    const taRef = useRef<HTMLTextAreaElement>(null)

    useEffect(() => {
        const el = taRef.current
        if (!el) return
        el.style.height = 'auto'
        const next = Math.min(el.scrollHeight, 200)
        el.style.height = `${next}px`
    }, [text])

    const submit = () => {
        const t = text.trim()
        if (!t || loading) return
        onSend(t)
        setText('')
    }

    const canSend = !loading && text.trim().length > 0

    return (
        <form
            className="relative flex items-end gap-2 rounded-2xl border border-line bg-surface px-3 py-2 shadow-[0_1px_0_0_rgba(255,255,255,0.03)_inset,0_8px_30px_-12px_rgba(0,0,0,0.6)] focus-within:border-line/80 focus-within:ring-1 focus-within:ring-accent/40 transition"
            onSubmit={(e) => { e.preventDefault(); submit() }}
        >
            <textarea
                ref={taRef}
                className="flex-1 resize-none bg-transparent text-ink placeholder:text-muted/60 text-[15px] leading-7 px-1 py-2 focus:outline-none disabled:opacity-60 max-h-[200px]"
                disabled={loading}
                rows={1}
                placeholder="輸入訊息…"
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={(e: CompositionKeyboardEvent) => {
                    const native = e.nativeEvent
                    if (native.isComposing || isComposing || native.keyCode === 229) return
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault()
                        submit()
                    }
                }}
                onCompositionStart={() => setIsComposing(true)}
                onCompositionEnd={() => setIsComposing(false)}
            />
            <button
                type="submit"
                aria-label="送出"
                disabled={!canSend}
                className="shrink-0 h-9 w-9 grid place-items-center rounded-lg bg-accent text-white transition hover:bg-accent-hover disabled:bg-elevated disabled:text-muted disabled:cursor-not-allowed"
            >
                <svg viewBox="0 0 20 20" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <path d="M10 16V4" />
                    <path d="M5 9l5-5 5 5" />
                </svg>
            </button>
        </form>
    )
}
