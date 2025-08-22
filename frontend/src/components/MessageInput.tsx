import React, { useState } from 'react'

export default function MessageInput({ loading, onSend }: { loading: boolean; onSend: (text: string) => void }) {
    const [text, setText] = useState('')
    const [isComposing, setIsComposing] = useState(false)

    const submit = () => {
        const t = text.trim()
        if (!t || loading) return
        onSend(t)
        setText('')
    }





    
    return (
        <form className="flex gap-2 items-end" onSubmit={(e) => { e.preventDefault(); submit() }}>
            <textarea
                className="flex-1 resize-none rounded-xl p-3 bg-slate-800/70 text-slate-100 border border-white/10 placeholder:text-slate-300/60 focus:outline-none focus:ring-2 focus:ring-cyan-400/40 focus:border-cyan-400/30 shadow-inner"
                disabled={loading}
                rows={2}
                placeholder="輸入訊息，按 Enter 送出，Shift+Enter 換行"
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={(e) => {
                    const native: any = e.nativeEvent as any
                    if (native?.isComposing || isComposing || native?.keyCode === 229) return
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault()
                        submit()
                    }
                }}
                onCompositionStart={() => setIsComposing(true)}
                onCompositionEnd={() => setIsComposing(false)}
            />
            <button className="px-4 py-2 rounded-lg bg-cyan-600/90 hover:bg-cyan-500/90 transition text-white disabled:opacity-50 border border-white/10 backdrop-blur-sm" type="submit" disabled={loading || !text.trim()}>
                送出
            </button>
        </form>
    )
}
