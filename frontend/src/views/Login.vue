<template>
  <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:#0f0f1a">
    <el-card style="width:420px;background:#1a1a2e;border:1px solid #2d2d44">
      <div style="text-align:center;margin-bottom:20px">
        <h1 style="color:#fff;margin:0 0 4px;font-size:22px">🛒 E-Shop AI</h1>
        <p style="color:#666;font-size:12px;margin:0">Smart Shopping Assistant</p>
      </div>
      <el-tabs v-model="mode" stretch>
        <el-tab-pane label="Login" name="login" />
        <el-tab-pane label="Register" name="register" />
      </el-tabs>
      <el-form label-position="top" @submit.prevent="submit">
        <el-form-item v-if="mode === 'register'" label="Username">
          <el-input v-model="username" placeholder="Username" />
        </el-form-item>
        <el-form-item label="Email">
          <el-input v-model="email" placeholder="you@example.com" />
        </el-form-item>
        <el-form-item label="Password">
          <el-input v-model="password" type="password" show-password placeholder="Password" @keyup.enter="submit" />
        </el-form-item>
        <el-button type="primary" style="width:100%" :loading="loading" @click="submit">
          {{ mode === "login" ? "Login" : "Create account" }}
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { authApi } from "@/api";
import { useAuthStore } from "@/stores/app";

const router = useRouter();
const authStore = useAuthStore();
const mode = ref<"login" | "register">("login");
const username = ref("");
const email = ref("");
const password = ref("");
const loading = ref(false);

async function submit() {
  if (!email.value || !password.value) {
    ElMessage.warning("Email and password are required");
    return;
  }
  if (mode.value === "register" && !username.value.trim()) {
    ElMessage.warning("Username is required");
    return;
  }
  loading.value = true;
  try {
    const res =
      mode.value === "login"
        ? await authApi.login(email.value, password.value)
        : await authApi.register(username.value.trim(), email.value, password.value);
    if (!res?.success) {
      ElMessage.error(res?.message || "Request failed");
      return;
    }
    authStore.login(
      { id: res.data.user_id, username: res.data.username, email: res.data.email },
      res.data.access_token
    );
    router.replace("/");
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || err?.message || "Request failed");
  } finally {
    loading.value = false;
  }
}
</script>
