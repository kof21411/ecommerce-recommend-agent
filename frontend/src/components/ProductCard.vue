<template>
  <el-card style="background:#1a1a2e;border:1px solid #2d2d44;cursor:pointer" shadow="hover">
    <div style="width:100%;height:160px;background:#2d2d44;border-radius:8px;display:flex;align-items:center;justify-content:center;margin-bottom:12px">
      <img v-if="product.image_url" :src="product.image_url" style="max-width:100%;max-height:100%;object-fit:contain" />
      <span v-else style="font-size:40px">📦</span>
    </div>
    <h4 style="color:#fff;margin:0 0 4px;font-size:14px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ product.name }}</h4>
    <div style="display:flex;align-items:baseline;gap:8px">
      <span style="color:#f56c6c;font-size:18px;font-weight:bold">¥{{ product.price }}</span>
      <span v-if="product.original_price" style="color:#666;font-size:12px;text-decoration:line-through">¥{{ product.original_price }}</span>
    </div>
    <div style="display:flex;justify-content:space-between;margin-top:8px;color:#666;font-size:12px">
      <span>⭐ {{ product.rating }}</span>
      <span>Sales: {{ product.sales_count }}</span>
    </div>
    <div v-if="product.brand" style="color:#409eff;font-size:11px;margin-top:4px">{{ product.brand }}</div>
  </el-card>
</template>
<script setup lang="ts">
import type { Product } from "@/types";
defineProps<{ product: Product }>();
</script>
