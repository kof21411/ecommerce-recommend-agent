<template>
  <div v-if="results.length > 0">
    <h3 style="color:#fff;margin-bottom:16px">🎯 Recommended Products</h3>
    <el-row :gutter="16">
      <el-col :span="8" v-for="(r, i) in results" :key="i">
        <el-card style="background:#1a1a2e;border:1px solid #2d2d44;margin-bottom:16px">
          <div style="display:flex;gap:12px">
            <div style="width:80px;height:80px;background:#2d2d44;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0">🛍️</div>
            <div style="flex:1;min-width:0">
              <h4 style="color:#fff;margin:0 0 4px;font-size:14px">{{ r.name }}</h4>
              <div style="color:#f56c6c;font-size:16px;font-weight:bold">¥{{ r.price }}</div>
              <div style="color:#67c23a;font-size:12px;margin-top:4px">Score: {{ r.score }}/10</div>
              <p style="color:#a0a3b1;font-size:12px;margin:8px 0 0;line-height:1.5">{{ r.reason }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup lang="ts">
defineProps<{ results: Array<{ name: string; price: number; score: number; reason: string }> }>();
</script>
