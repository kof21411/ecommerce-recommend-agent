<template>
  <div style="display:flex;flex-direction:column;height:100%;background:#1a1a2e;border-radius:12px;border:1px solid #2d2d44">
    <div style="padding:16px;border-bottom:1px solid #2d2d44">
      <h3 style="color:#fff;margin:0;font-size:15px">🛒 Shopping Assistant</h3>
      <p style="color:#666;font-size:12px;margin:4px 0 0">Ask me anything about products</p>
    </div>
    <div ref="messagesRef" style="flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:12px">
      <div v-if="chatStore.messages.length === 0 && !chatStore.isGenerating" style="text-align:center;padding:40px 0;color:#666">
        <div style="font-size:48px;margin-bottom:16px">🛒</div>
        <p>How can I help you shop today?</p>
        <div style="display:flex;gap:8px;justify-content:center;margin-top:16px;flex-wrap:wrap">
          <el-button @click="quick('Recommend wireless earbuds under 500 yuan')">🎧 Earbuds</el-button>
          <el-button @click="quick('Best phones under 3000 yuan in 2026')">📱 Phones</el-button>
          <el-button @click="quick('Compare mechanical keyboards')">⌨️ Compare</el-button>
        </div>
      </div>
      <div v-for="msg in chatStore.messages" :key="msg.id" :style="{display:'flex',justifyContent:msg.role==='user'?'flex-end':'flex-start'}">
        <div :style="{maxWidth:'80%',padding:'10px 14px',borderRadius:'16px',fontSize:'13px',lineHeight:'1.6',whiteSpace:'pre-wrap',background:msg.role==='user'?'#409eff':'#2d2d44',color:msg.role==='user'?'#fff':'#e0e0e0'}">{{ msg.content }}</div>
      </div>
      <div v-if="chatStore.isGenerating && chatStore.streamingText" style="display:flex">
        <div style="max-width:80%;padding:10px 14px;border-radius:16px;background:#2d2d44;color:#e0e0e0;font-size:13px;white-space:pre-wrap">{{ chatStore.streamingText }}<span style="animation:blink 1s infinite">|</span></div>
      </div>
      <div v-if="chatStore.isGenerating && !chatStore.streamingText" style="color:#666;font-size:12px">Thinking...</div>
      <el-row v-if="products.length" :gutter="12">
        <el-col v-for="item in products" :key="item.product.id" :span="8"><ProductCard :product="item.product" /><p>{{ item.reason }}</p></el-col>
      </el-row>
    </div>
    <div style="padding:12px 16px;border-top:1px solid #2d2d44;display:flex;gap:8px">
      <el-input v-model="input" type="textarea" :rows="2" placeholder="What are you looking for?" :disabled="chatStore.isGenerating" @keydown.enter.exact.prevent="send" style="flex:1" />
      <el-button type="primary" @click="send" :disabled="!input.trim() || chatStore.isGenerating">Send</el-button>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, nextTick, watch, onMounted } from "vue";
import { useChatStore } from "@/stores/app";
import { chatApi } from "@/api";
import ProductCard from "@/components/ProductCard.vue";
import type { RecommendResult } from "@/types";

const chatStore = useChatStore();
const input = ref("");
const products = ref<RecommendResult[]>([]);
const messagesRef = ref<HTMLDivElement>();

function scrollToBottom() {
  nextTick(() => messagesRef.value?.scrollTo(0, messagesRef.value.scrollHeight));
}

watch([() => chatStore.messages.length, () => chatStore.streamingText], scrollToBottom);

onMounted(async () => {
  try {
    const res = await chatApi.getHistory();
    if (res?.success && res.data?.length) chatStore.setMessages(res.data);
  } catch {
    /* history is optional */
  }
});

async function send() {
  const msg = input.value.trim();
  if (!msg || chatStore.isGenerating) return;
  chatStore.addMessage({ id: crypto.randomUUID(), role: "user", content: msg, created_at: new Date().toISOString() });
  input.value = "";
  chatStore.startGenerating();
  products.value = [];
  await chatApi.sendMessageStream(
    msg,
    (c) => chatStore.appendText(c),
    () =>
      chatStore.finishGenerating({
        id: crypto.randomUUID(),
        role: "assistant",
        content: chatStore.streamingText || "(empty response)",
        created_at: new Date().toISOString(),
      }),
    (e) =>
      chatStore.finishGenerating({
        id: crypto.randomUUID(),
        role: "assistant",
        content: "Error: " + e,
        created_at: new Date().toISOString(),
      }),
    (items) => { products.value = items; }
  );
}
function quick(t: string) {
  input.value = t;
  send();
}
</script>
<style>
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
</style>
