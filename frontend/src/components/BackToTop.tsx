import React, { useEffect, useState } from 'react'

export default function BackToTop() {
    const [visible, setVisible] = useState(false)

    useEffect(() => {
        const onScroll = () => {
            setVisible(window.scrollY > 200)
        }
        window.addEventListener('scroll', onScroll)
        onScroll()
        return () => window.removeEventListener('scroll', onScroll)
    }, [])

    const scrollTop = () => {
        window.scrollTo({ top: 0, behavior: 'smooth' })
    }

    if (!visible) return null

    return (
        <button
            onClick={scrollTop}
            aria-label="Back to top"
            className="fixed bottom-6 right-6 h-10 w-10 rounded-full bg-cyan-600/90 hover:bg-cyan-500/90 text-white shadow-lg border border-white/10 backdrop-blur-sm"
            title="回到頂端"
        >
            ↑
        </button>
    )
}
