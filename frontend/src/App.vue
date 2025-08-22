<template>
    <div class="relative min-h-screen bg-slate-950 text-slate-50">
        <LiquidBackground />
        <div class="max-w-3xl mx-auto px-4 py-10">
            <h1 class="text-3xl font-semibold text-slate-100 mb-6 drop-shadow-sm">FutureNest Chat</h1>
            <div class="rounded-2xl bg-white/10 backdrop-blur-xl shadow-2xl p-5 border border-white/20">
                <ChatContainer />
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import ChatContainer from './components/ChatContainer.vue'
import LiquidBackground from './components/LiquidBackground.vue'
export { }
</script>

<style>
/* 可補充全域樣式 */
</style>
