-- E-commerce Recommendation Agent - PostgreSQL 15+
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(500),
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_users_email ON users(email);

-- 商品分类表
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    parent_id UUID REFERENCES categories(id),
    icon VARCHAR(50),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 商品表
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(300) NOT NULL,
    description TEXT,
    price NUMERIC(10,2) NOT NULL,
    original_price NUMERIC(10,2),
    category_id UUID REFERENCES categories(id),
    brand VARCHAR(100),
    image_url VARCHAR(500),
    attributes JSONB DEFAULT '{}',
    stock INTEGER DEFAULT 0,
    sales_count INTEGER DEFAULT 0,
    rating FLOAT DEFAULT 0,
    review_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_name_trgm ON products USING gin(name gin_trgm_ops);

-- 用户画像表
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    interests JSONB DEFAULT '{}',
    behavior JSONB DEFAULT '{}',
    price_range JSONB DEFAULT '{}',
    preferred_brands JSONB DEFAULT '[]',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 商品浏览记录
CREATE TABLE product_views (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    duration_seconds INTEGER DEFAULT 0,
    action VARCHAR(20) DEFAULT 'view',
    viewed_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_views_user ON product_views(user_id);
CREATE INDEX idx_views_product ON product_views(product_id);

-- 订单表
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_price NUMERIC(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    items JSONB DEFAULT '[]',
    address JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 对话消息表
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_chat_user ON chat_messages(user_id, created_at);

-- 知识库文档表
CREATE TABLE knowledge_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    product_id UUID,
    source VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 推荐记录表
CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    product_ids JSONB DEFAULT '[]',
    explanation TEXT,
    clicked JSONB DEFAULT '[]',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 自动更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column() RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 示例分类数据
INSERT INTO categories (name, icon, sort_order) VALUES
('Electronics', '💻', 1), ('Audio', '🎧', 2), ('Phones', '📱', 3),
('Computers', '🖥️', 4), ('Fashion', '👕', 5), ('Home', '🏠', 6);

-- 示例知识库数据
INSERT INTO knowledge_documents (title, content, category) VALUES
('Wireless Earbuds Buying Guide', 'Key factors: battery life, noise cancellation, comfort, sound quality, IPX rating for sports.', 'guide'),
('Smartphone Comparison 2026', 'Flagship phones: Camera quality, processor speed, battery, display refresh rate, 5G support.', 'comparison'),
('Mechanical Keyboard Guide', 'Switch types: Linear (Cherry MX Red), Tactile (Brown), Clicky (Blue). Keycap material matters.', 'guide'),
('Laptop Buying Guide 2026', 'Consider: CPU generation, RAM (16GB min), SSD speed, display quality, weight, battery life.', 'guide'),
('Audio Equipment Review', 'Headphones vs earbuds vs speakers: Use case determines best choice. ANC worth it for commuters.', 'review');
