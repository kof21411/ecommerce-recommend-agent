import axios from "axios";
import type { PaginatedResponse } from "../types";

// 开发环境走 Vite 代理，生产环境走 Nginx 反向代理，均使用同源相对路径
const API_BASE = import.meta.env.VITE_API_URL || "";
const client = axios.create({ baseURL: API_BASE, timeout: 60000 });
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
client.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("access_token");
      if (window.location.pathname !== "/login") window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export const authApi = {
  async login(email: string, password: string) {
    return (await client.post("/api/auth/login", { email, password })).data;
  },
  async register(username: string, email: string, password: string) {
    return (await client.post("/api/auth/register", { username, email, password })).data;
  },
  async me() {
    return (await client.get("/api/auth/me")).data;
  },
};

export const productApi = {
  async create(product: { name: string; description?: string; price: number; stock: number; brand?: string }) {
    return (await client.post("/api/products/", product)).data;
  },
  async list(params: {
    keyword?: string;
    category_id?: string;
    min_price?: number;
    max_price?: number;
    brand?: string;
    sort_by?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse> {
    return (await client.get("/api/products/", { params })).data;
  },
  async getDetail(id: string) {
    return (await client.get(`/api/products/${id}`)).data;
  },
  async getCategories() {
    return (await client.get("/api/products/categories/list")).data;
  },
};

export const recommendApi = {
  async recommend(payload: { query: string; budget?: number; category?: string }) {
    return (await client.post("/api/recommend/", payload)).data;
  },
};

export const chatApi = {
  async sendMessageStream(
    message: string,
    onChunk: (c: string) => void,
    onDone: (a: string) => void,
    onError: (e: string) => void,
    onProducts?: (items: import("../types").RecommendResult[]) => void
  ) {
    const token = localStorage.getItem("access_token");
    const response = await fetch(`${API_BASE}/api/chat/`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ message, stream: true }),
    });
    if (!response.ok) {
      onError(`HTTP ${response.status}`);
      return;
    }
    const reader = response.body?.getReader();
    if (!reader) {
      onError("No reader");
      return;
    }
    const decoder = new TextDecoder();
    let buffer = "";
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const evt = JSON.parse(line.slice(6));
              if (evt.type === "chunk") onChunk(evt.content || "");
              else if (evt.type === "products" && Array.isArray(evt.items)) onProducts?.(evt.items);
              else if (evt.type === "done") onDone(evt.action || "completed");
              else if (evt.type === "error") onError(evt.message || "Error");
            } catch {
              /* ignore malformed event */
            }
          }
        }
      }
    } catch (err) {
      onError(String(err));
    }
  },
  async getHistory(limit = 50) {
    return (await client.get(`/api/chat/history?limit=${limit}`)).data;
  },
};
export { client };
