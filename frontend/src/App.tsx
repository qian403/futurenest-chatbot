import React from 'react'
import ChatContainer from './components/ChatContainer'
import BackToTop from './components/BackToTop'
import LiquidBackground from './components/LiquidBackground'

export default function App() {
    return (
        <div className="relative min-h-screen bg-slate-950 text-slate-50">
            <LiquidBackground />
            <div className="max-w-3xl mx-auto px-4 py-10">
                <h1 className="text-3xl font-semibold text-slate-100 mb-6 drop-shadow-sm">FutureNest Chat</h1>
                <div className="rounded-2xl bg-white/10 backdrop-blur-xl shadow-2xl p-5 border border-white/20">
                    <ChatContainer />
                </div>
            </div>
            <BackToTop />
        </div>
    )
}
