export interface User {
  id: string;
  username: string;
  email: string;
}
export interface Product {
  id: string;
  name: string;
  description?: string;
  price: number;
  original_price?: number;
  brand?: string;
  image_url?: string;
  rating: number;
  review_count: number;
  sales_count: number;
  stock: number;
  attributes?: Record<string, any>;
}
export interface Category {
  id: string;
  name: string;
  parent_id?: string;
  icon?: string;
}
export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
}
export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
}
export interface PaginatedResponse<T = any> {
  success: boolean;
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
export interface RecommendResult {
  product: Product;
  score: number;
  reason: string;
}
