<template>
  <div>
    <el-button @click="showCreate = !showCreate" style="margin-bottom:16px">添加商品（管理员）</el-button>
    <el-form v-if="showCreate" style="max-width:500px;margin-bottom:20px" label-position="top">
      <el-form-item label="名称"><el-input v-model="newProduct.name" /></el-form-item>
      <el-form-item label="描述"><el-input v-model="newProduct.description" type="textarea" /></el-form-item>
      <el-form-item label="价格"><el-input-number v-model="newProduct.price" :min="0" /></el-form-item>
      <el-form-item label="库存"><el-input-number v-model="newProduct.stock" :min="0" /></el-form-item>
      <el-form-item label="品牌"><el-input v-model="newProduct.brand" /></el-form-item>
      <el-button type="primary" @click="createProduct">保存</el-button>
    </el-form>
    <div style="display:flex;gap:16px;margin-bottom:20px;align-items:center">
      <el-input v-model="keyword" placeholder="Search products..." clearable @keyup.enter="loadProducts" style="max-width:400px">
        <template #append><el-button @click="loadProducts">Search</el-button></template>
      </el-input>
      <el-select v-model="sortBy" @change="loadProducts" style="width:150px">
        <el-option label="Sales" value="sales" />
        <el-option label="Price Low" value="price_asc" />
        <el-option label="Price High" value="price_desc" />
        <el-option label="Rating" value="rating" />
      </el-select>
    </div>
    <el-row :gutter="16">
      <el-col :span="6" v-for="p in productStore.products" :key="p.id">
        <ProductCard :product="p" />
      </el-col>
    </el-row>
    <el-empty v-if="productStore.products.length === 0" description="No products found" />
    <el-pagination
      v-if="total > pageSize"
      :current-page="page"
      :page-size="pageSize"
      :total="total"
      layout="prev, pager, next"
      @current-change="(p: number) => { page = p; loadProducts(); }"
      style="margin-top:20px;justify-content:center"
    />
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useProductStore } from "@/stores/app";
import { productApi } from "@/api";
import ProductCard from "@/components/ProductCard.vue";
import { ElMessage } from "element-plus";

const productStore = useProductStore();
const keyword = ref("");
const sortBy = ref("sales");
const page = ref(1);
const pageSize = 20;
const total = ref(0);
const showCreate = ref(false);
const newProduct = ref({ name: "", description: "", price: 0, stock: 0, brand: "" });

async function createProduct() {
  try {
    const response = await productApi.create(newProduct.value);
    ElMessage.success(response.data.index_status === "indexed" ? "商品已创建并索引" : `商品已创建，索引失败，请重试：${response.data.id}`);
    showCreate.value = false;
    await loadProducts();
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || "创建失败");
  }
}

async function loadProducts() {
  productStore.loading = true;
  try {
    const r = await productApi.list({
      keyword: keyword.value || undefined,
      sort_by: sortBy.value,
      page: page.value,
      page_size: pageSize,
    });
    if (r.success) {
      productStore.setProducts(r.items);
      total.value = r.total;
    }
  } finally {
    productStore.loading = false;
  }
}
onMounted(loadProducts);
</script>
