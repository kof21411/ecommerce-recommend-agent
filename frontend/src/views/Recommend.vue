<template>
  <div>
    <h2 style="color:#fff;margin:0 0 8px">AI Recommendation</h2>
    <p style="color:#666;margin-bottom:20px">Tell us what you're looking for, and AI will find the best products for you.</p>
    <el-input
      v-model="query"
      type="textarea"
      :rows="3"
      placeholder="Example: I need wireless earbuds under 500 yuan for running, good bass..."
      style="max-width:700px;margin-bottom:16px"
    />
    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="6"><el-input v-model="budget" placeholder="Budget (yuan)" clearable /></el-col>
      <el-col :span="6"><el-input v-model="category" placeholder="Category" clearable /></el-col>
      <el-col :span="6">
        <el-button type="primary" @click="handleRecommend" :loading="loading">Get Recommendations</el-button>
      </el-col>
    </el-row>
    <el-card v-if="result" style="background:#1a1a2e;border:1px solid #2d2d44;max-width:900px">
      <h3 style="color:#fff;margin:0 0 12px">Recommended for you</h3>
      <div style="color:#d0d3dc;font-size:13px;line-height:1.8;white-space:pre-wrap">{{ result }}</div>
    </el-card>
    <el-alert v-if="degraded" title="检索或排序已降级" type="warning" :closable="false" />
    <el-row :gutter="16" style="margin-top:16px">
      <el-col v-for="item in items" :key="item.product.id" :span="8">
        <ProductCard :product="item.product" />
        <p style="color:#a0a3b1;margin:8px 0 16px">{{ item.reason }}</p>
      </el-col>
    </el-row>
    <el-empty v-if="!result && !loading" description="No recommendation yet" />
  </div>
</template>
<script setup lang="ts">
import { ref } from "vue";
import { ElMessage } from "element-plus";
import { recommendApi } from "@/api";
import ProductCard from "@/components/ProductCard.vue";
import type { RecommendResult } from "@/types";

const query = ref("");
const budget = ref("");
const category = ref("");
const loading = ref(false);
const result = ref("");
const items = ref<RecommendResult[]>([]);
const degraded = ref(false);

async function handleRecommend() {
  if (!query.value.trim()) {
    ElMessage.warning("Please describe what you need");
    return;
  }
  loading.value = true;
  result.value = "";
  items.value = [];
  try {
    const res = await recommendApi.recommend({
      query: query.value.trim(),
      budget: budget.value ? Number(budget.value) : undefined,
      category: category.value || undefined,
    });
    result.value = res?.data?.content || "";
    items.value = res?.data?.items || [];
    degraded.value = !!res?.data?.degraded;
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || err?.message || "Recommendation failed");
  } finally {
    loading.value = false;
  }
}
</script>
