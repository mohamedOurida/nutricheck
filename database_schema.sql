-- Supabase SQL for creating the zara_products table
-- Run this in the Supabase SQL editor

-- Create table for storing Zara products
CREATE TABLE IF NOT EXISTS public.zara_products (
    id BIGSERIAL PRIMARY KEY,
    product_id TEXT UNIQUE NOT NULL,
    name TEXT,
    price DECIMAL(10,2),
    price_text TEXT,
    image_url TEXT,
    product_url TEXT,
    color TEXT,
    source TEXT DEFAULT 'zara',
    category TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    scraped_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_zara_products_product_id ON public.zara_products(product_id);
CREATE INDEX IF NOT EXISTS idx_zara_products_created_at ON public.zara_products(created_at);
CREATE INDEX IF NOT EXISTS idx_zara_products_category ON public.zara_products(category);

-- Enable Row Level Security (RLS)
ALTER TABLE public.zara_products ENABLE ROW LEVEL SECURITY;

-- Create policy to allow service role to do everything
CREATE POLICY "Enable all access for service role" ON public.zara_products
FOR ALL USING (auth.role() = 'service_role');

-- Create policy to allow authenticated users to read
CREATE POLICY "Enable read access for authenticated users" ON public.zara_products
FOR SELECT USING (auth.role() = 'authenticated');

-- Add comments to the table and columns
COMMENT ON TABLE public.zara_products IS 'Table storing scraped Zara product data';
COMMENT ON COLUMN public.zara_products.product_id IS 'Unique product identifier from Zara';
COMMENT ON COLUMN public.zara_products.name IS 'Product name';
COMMENT ON COLUMN public.zara_products.price IS 'Product price as decimal';
COMMENT ON COLUMN public.zara_products.price_text IS 'Original price text from website';
COMMENT ON COLUMN public.zara_products.image_url IS 'URL to product image';
COMMENT ON COLUMN public.zara_products.product_url IS 'URL to product page';
COMMENT ON COLUMN public.zara_products.color IS 'Product color/variant';
COMMENT ON COLUMN public.zara_products.source IS 'Source of the data (always zara)';
COMMENT ON COLUMN public.zara_products.category IS 'Product category (e.g., homme, femme)';
COMMENT ON COLUMN public.zara_products.created_at IS 'When the record was first created';
COMMENT ON COLUMN public.zara_products.updated_at IS 'When the record was last updated';
COMMENT ON COLUMN public.zara_products.scraped_at IS 'When the product was scraped from the website';