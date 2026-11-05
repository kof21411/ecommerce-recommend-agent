import { createRouter, createWebHistory } from "vue-router";

const routes = [
  { path: "/login", name: "Login", component: () => import("@/views/Login.vue") },
  { path: "/", name: "Dashboard", component: () => import("@/views/Dashboard.vue") },
  { path: "/products", name: "ProductList", component: () => import("@/views/ProductList.vue") },
  { path: "/recommend", name: "Recommend", component: () => import("@/views/Recommend.vue") },
  { path: "/chat", name: "Chat", component: () => import("@/views/Chat.vue") },
  { path: "/:pathMatch(.*)*", redirect: "/" },
];

const router = createRouter({ history: createWebHistory(), routes });

router.beforeEach((to) => {
  const token = localStorage.getItem("access_token");
  if (to.path !== "/login" && !token) return "/login";
  if (to.path === "/login" && token) return "/";
});

export default router;
