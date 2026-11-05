import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { User, Product, ChatMessage } from "../types";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<User | null>(null);
  const token = ref<string | null>(localStorage.getItem("access_token"));
  const isAuthenticated = computed(() => !!token.value);
  function login(u: User, t: string) {
    user.value = u;
    token.value = t;
    localStorage.setItem("access_token", t);
  }
  function logout() {
    user.value = null;
    token.value = null;
    localStorage.removeItem("access_token");
  }
  return { user, token, isAuthenticated, login, logout };
});

export const useProductStore = defineStore("product", () => {
  const products = ref<Product[]>([]);
  const categories = ref<any[]>([]);
  const loading = ref(false);
  function setProducts(p: Product[]) {
    products.value = p;
  }
  function setCategories(c: any[]) {
    categories.value = c;
  }
  return { products, categories, loading, setProducts, setCategories };
});

export const useChatStore = defineStore("chat", () => {
  const messages = ref<ChatMessage[]>([]);
  const isGenerating = ref(false);
  const streamingText = ref("");
  function addMessage(m: ChatMessage) {
    messages.value.push(m);
  }
  function setMessages(l: ChatMessage[]) {
    messages.value = l;
  }
  function startGenerating() {
    isGenerating.value = true;
    streamingText.value = "";
  }
  function appendText(t: string) {
    streamingText.value += t;
  }
  function finishGenerating(m: ChatMessage) {
    isGenerating.value = false;
    streamingText.value = "";
    messages.value.push(m);
  }
  function clearMessages() {
    messages.value = [];
    streamingText.value = "";
  }
  return {
    messages,
    isGenerating,
    streamingText,
    addMessage,
    setMessages,
    startGenerating,
    appendText,
    finishGenerating,
    clearMessages,
  };
});
