import React from 'react'
import ChatContainer from './components/ChatContainer'
import BackToTop from './components/BackToTop'

export default function App() {
    return (
        <div className="min-h-screen bg-canvas text-ink font-sans antialiased">
            <ChatContainer />
            <BackToTop />
        </div>
    )
}
