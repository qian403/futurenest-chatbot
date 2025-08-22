import React from 'react'

export default function LiquidBackground() {
    return (
        <div className="absolute inset-0 -z-10 overflow-hidden">
            <div className="absolute -top-20 -left-20 h-72 w-72 bg-blue-500/20 rounded-full blur-3xl animate-blob" />
            <div className="absolute top-10 -right-10 h-64 w-64 bg-violet-500/20 rounded-full blur-3xl animate-blob [animation-delay:2s]" />
            <div className="absolute bottom-0 left-1/3 h-80 w-80 bg-cyan-500/20 rounded-full blur-3xl animate-blob [animation-delay:4s]" />
        </div>
    )
}
