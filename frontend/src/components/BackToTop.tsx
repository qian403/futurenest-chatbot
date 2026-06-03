import React, { useEffect, useState } from 'react'

function getScroller(): HTMLElement | Window {
    const main = document.querySelector('main')
    if (main && main.scrollHeight > main.clientHeight) return main
    return window
}

export default function BackToTop() {
    const [visible, setVisible] = useState(false)

    useEffect(() => {
        const scroller = getScroller()
        const readTop = () =>
            scroller instanceof Window ? scroller.scrollY : scroller.scrollTop
        const onScroll = () => setVisible(readTop() > 200)
        scroller.addEventListener('scroll', onScroll, { passive: true })
        onScroll()
        return () => scroller.removeEventListener('scroll', onScroll)
    }, [])

    const scrollTop = () => {
        const scroller = getScroller()
        if (scroller instanceof Window) {
            scroller.scrollTo({ top: 0, behavior: 'smooth' })
        } else {
            scroller.scrollTo({ top: 0, behavior: 'smooth' })
        }
    }

    if (!visible) return null

    return (
        <button
            onClick={scrollTop}
            aria-label="回到頂端"
            title="回到頂端"
            className="fixed bottom-24 right-6 h-9 w-9 grid place-items-center rounded-full bg-surface border border-line text-muted hover:text-ink hover:border-line/80 transition shadow-lg"
        >
            <svg viewBox="0 0 20 20" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M10 16V4" />
                <path d="M5 9l5-5 5 5" />
            </svg>
        </button>
    )
}
