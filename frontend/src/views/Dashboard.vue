<template>
  <div>
    <h2 style="color:#fff;margin:0 0 20px">Dashboard</h2>
    <el-row :gutter="16">
      <el-col :span="6" v-for="stat in stats" :key="stat.label">
        <el-card style="background:#1a1a2e;border:1px solid #2d2d44">
          <div style="font-size:24px;margin-bottom:8px">{{ stat.icon }}</div>
          <div style="font-size:20px;font-weight:bold;color:#fff">{{ stat.value }}</div>
          <div style="font-size:12px;color:#666;margin-top:4px">{{ stat.label }}</div>
        </el-card>
      </el-col>
    </el-row>
    <h3 style="color:#fff;margin:24px 0 16px">Quick Actions</h3>
    <el-row :gutter="16">
      <el-col :span="6" v-for="action in actions" :key="action.label">
        <el-card style="background:#1a1a2e;border:1px solid #2d2d44;cursor:pointer" @click="$router.push(action.path)">
          <div style="text-align:center;padding:20px 0">
            <div style="font-size:32px;margin-bottom:12px">{{ action.icon }}</div>
            <div style="color:#fff;font-size:14px">{{ action.label }}</div>
            <div style="color:#666;font-size:12px;margin-top:4px">{{ action.desc }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup lang="ts">
const stats = [
  { icon: "📦", value: "12,580", label: "Products" },
  { icon: "👥", value: "3,240", label: "Users" },
  { icon: "🛒", value: "856", label: "Orders Today" },
  { icon: "⭐", value: "4.8", label: "Avg Rating" },
];
const actions = [
  { icon: "🔍", label: "Search Products", desc: "Find what you need", path: "/products" },
  { icon: "🎯", label: "Get Recommendations", desc: "AI personalized picks", path: "/recommend" },
  { icon: "💬", label: "AI Chat", desc: "Ask shopping questions", path: "/chat" },
  { icon: "📊", label: "Browse Categories", desc: "Explore by category", path: "/products" },
];
</script>
