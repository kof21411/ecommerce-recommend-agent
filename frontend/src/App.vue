<template>
  <router-view v-if="$route.path === '/login'" />
  <el-container v-else style="height:100vh">
    <el-aside width="220px" style="background:#1a1a2e;border-right:1px solid #2d2d44">
      <div style="padding:24px 16px;border-bottom:1px solid #2d2d44">
        <h1 style="font-size:18px;color:#fff;margin:0">🛒 E-Shop AI</h1>
        <p style="font-size:12px;color:#666;margin-top:4px">Smart Shopping Assistant</p>
      </div>
      <el-menu :default-active="$route.path" router background-color="#1a1a2e" text-color="#a0a3b1" active-text-color="#409eff">
        <el-menu-item index="/"><el-icon><DataBoard /></el-icon><span>Dashboard</span></el-menu-item>
        <el-menu-item index="/products"><el-icon><ShoppingBag /></el-icon><span>Products</span></el-menu-item>
        <el-menu-item index="/recommend"><el-icon><MagicStick /></el-icon><span>Recommend</span></el-menu-item>
        <el-menu-item index="/chat"><el-icon><ChatDotRound /></el-icon><span>AI Chat</span></el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="background:#1a1a2e;border-bottom:1px solid #2d2d44;display:flex;align-items:center;justify-content:space-between;color:#a0a3b1">
        <span>{{ $route.path }}</span>
        <el-button text @click="handleLogout">Logout</el-button>
      </el-header>
      <el-main style="background:#0f0f1a;padding:20px"><router-view /></el-main>
    </el-container>
  </el-container>
</template>
<script setup lang="ts">
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/app";
import { DataBoard, ShoppingBag, MagicStick, ChatDotRound } from "@element-plus/icons-vue";

const authStore = useAuthStore();
const router = useRouter();

function handleLogout() {
  authStore.logout();
  router.replace("/login");
}
</script>
