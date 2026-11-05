<template>
  <el-card style="background:#1a1a2e;border:1px solid #2d2d44">
    <h4 style="color:#fff;margin:0 0 12px">Filters</h4>
    <el-form label-position="top">
      <el-form-item label="Price Range">
        <el-row :gutter="8">
          <el-col :span="11"><el-input v-model="filters.minPrice" placeholder="Min" /></el-col>
          <el-col :span="2" style="text-align:center;color:#666">-</el-col>
          <el-col :span="11"><el-input v-model="filters.maxPrice" placeholder="Max" /></el-col>
        </el-row>
      </el-form-item>
      <el-form-item label="Brand">
        <el-select v-model="filters.brand" clearable placeholder="All brands" style="width:100%">
          <el-option v-for="b in brands" :key="b" :label="b" :value="b" />
        </el-select>
      </el-form-item>
      <el-form-item label="Rating">
        <el-rate v-model="filters.rating" :min="0" :max="5" />
      </el-form-item>
      <el-button type="primary" @click="$emit('filter', filters)" style="width:100%">Apply</el-button>
    </el-form>
  </el-card>
</template>
<script setup lang="ts">
import { reactive } from "vue";
const filters = reactive({ minPrice: "", maxPrice: "", brand: "", rating: 0 });
const brands = ["Apple", "Samsung", "Sony", "Xiaomi", "Huawei", "Bose"];
defineEmits<{ filter: [f: { minPrice: string; maxPrice: string; brand: string; rating: number }] }>();
</script>
