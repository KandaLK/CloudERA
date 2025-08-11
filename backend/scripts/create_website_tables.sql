-- Migration script for website functionality tables (Normalized Architecture)
-- Run this after the existing user tables are created

-- ====================================
-- CORE TABLES
-- ====================================

-- Categories table - Post categorization
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    color VARCHAR(7) DEFAULT '#3B82F6',
    icon VARCHAR(50),
    parent_id UUID,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- Tags table - Flexible tagging system
CREATE TABLE IF NOT EXISTS tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    color VARCHAR(7) DEFAULT '#6B7280',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Posts table - Core post content
CREATE TABLE IF NOT EXISTS posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    summary TEXT NOT NULL,
    author_id UUID NOT NULL,
    category_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

-- ====================================
-- POST-RELATED TABLES
-- ====================================

-- Post metadata - Publishing and SEO information
CREATE TABLE IF NOT EXISTS post_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID UNIQUE NOT NULL,
    is_featured BOOLEAN DEFAULT FALSE,
    is_published BOOLEAN DEFAULT TRUE,
    published_at TIMESTAMPTZ DEFAULT NOW(),
    reading_time_minutes INTEGER DEFAULT 0,
    seo_title VARCHAR(255),
    seo_description VARCHAR(500),
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

-- Post engagement - Analytics and metrics
CREATE TABLE IF NOT EXISTS post_engagement (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID UNIQUE NOT NULL,
    views_count INTEGER DEFAULT 0,
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    last_viewed_at TIMESTAMPTZ,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

-- Post media - Images, videos, files
CREATE TABLE IF NOT EXISTS post_media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL,
    media_type VARCHAR(20) NOT NULL, -- image, video, file
    url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(255),
    caption TEXT,
    file_size INTEGER,
    mime_type VARCHAR(100),
    is_primary BOOLEAN DEFAULT FALSE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

-- Post tags relationship
CREATE TABLE IF NOT EXISTS post_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL,
    tag_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    UNIQUE(post_id, tag_id)
);

-- Post likes - User engagement
CREATE TABLE IF NOT EXISTS post_likes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    post_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    UNIQUE(user_id, post_id)
);

-- ====================================
-- USER-RELATED TABLES
-- ====================================

-- User profiles - Extended user information
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL,
    display_name VARCHAR(100),
    full_name VARCHAR(150),
    bio TEXT,
    location VARCHAR(100),
    timezone VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- User avatars - Profile images
CREATE TABLE IF NOT EXISTS user_avatars (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID UNIQUE NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    file_size INTEGER,
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (profile_id) REFERENCES user_profiles(id) ON DELETE CASCADE
);

-- User social links - Social media profiles
CREATE TABLE IF NOT EXISTS user_social_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    platform VARCHAR(50) NOT NULL, -- github, linkedin, twitter, website
    url VARCHAR(500) NOT NULL,
    display_text VARCHAR(100),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (profile_id) REFERENCES user_profiles(id) ON DELETE CASCADE
);

-- User permissions - Role-based access control
CREATE TABLE IF NOT EXISTS user_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    permission_type VARCHAR(50) NOT NULL, -- admin, editor, author, subscriber
    resource_type VARCHAR(50), -- posts, users, categories, etc.
    resource_id UUID, -- Specific resource ID if applicable
    granted_by UUID,
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (profile_id) REFERENCES user_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES users(id) ON DELETE SET NULL
);

-- ====================================
-- INDEXES FOR PERFORMANCE
-- ====================================

-- Posts table indexes
CREATE INDEX IF NOT EXISTS idx_posts_author_id ON posts(author_id);
CREATE INDEX IF NOT EXISTS idx_posts_category_id ON posts(category_id);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_posts_updated_at ON posts(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_posts_slug ON posts(slug);
CREATE INDEX IF NOT EXISTS idx_posts_title ON posts USING gin(to_tsvector('english', title));

-- Post metadata indexes
CREATE INDEX IF NOT EXISTS idx_post_metadata_post_id ON post_metadata(post_id);
CREATE INDEX IF NOT EXISTS idx_post_metadata_is_featured ON post_metadata(is_featured);
CREATE INDEX IF NOT EXISTS idx_post_metadata_is_published ON post_metadata(is_published);
CREATE INDEX IF NOT EXISTS idx_post_metadata_published_at ON post_metadata(published_at DESC);

-- Post engagement indexes
CREATE INDEX IF NOT EXISTS idx_post_engagement_post_id ON post_engagement(post_id);
CREATE INDEX IF NOT EXISTS idx_post_engagement_views_count ON post_engagement(views_count DESC);
CREATE INDEX IF NOT EXISTS idx_post_engagement_likes_count ON post_engagement(likes_count DESC);

-- Post media indexes
CREATE INDEX IF NOT EXISTS idx_post_media_post_id ON post_media(post_id);
CREATE INDEX IF NOT EXISTS idx_post_media_is_primary ON post_media(is_primary);
CREATE INDEX IF NOT EXISTS idx_post_media_media_type ON post_media(media_type);

-- Post tags indexes
CREATE INDEX IF NOT EXISTS idx_post_tags_post_id ON post_tags(post_id);
CREATE INDEX IF NOT EXISTS idx_post_tags_tag_id ON post_tags(tag_id);

-- Post likes indexes
CREATE INDEX IF NOT EXISTS idx_post_likes_user_id ON post_likes(user_id);
CREATE INDEX IF NOT EXISTS idx_post_likes_post_id ON post_likes(post_id);
CREATE INDEX IF NOT EXISTS idx_post_likes_created_at ON post_likes(created_at DESC);

-- Categories indexes
CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);
CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug);
CREATE INDEX IF NOT EXISTS idx_categories_parent_id ON categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_categories_is_active ON categories(is_active);

-- Tags indexes
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);
CREATE INDEX IF NOT EXISTS idx_tags_slug ON tags(slug);

-- User profiles indexes
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_display_name ON user_profiles(display_name);

-- User social links indexes
CREATE INDEX IF NOT EXISTS idx_user_social_links_profile_id ON user_social_links(profile_id);
CREATE INDEX IF NOT EXISTS idx_user_social_links_platform ON user_social_links(platform);

-- User permissions indexes
CREATE INDEX IF NOT EXISTS idx_user_permissions_profile_id ON user_permissions(profile_id);
CREATE INDEX IF NOT EXISTS idx_user_permissions_permission_type ON user_permissions(permission_type);
CREATE INDEX IF NOT EXISTS idx_user_permissions_is_active ON user_permissions(is_active);

-- ====================================
-- TRIGGERS AND FUNCTIONS
-- ====================================\n\n-- Function for updating updated_at column\nCREATE OR REPLACE FUNCTION update_updated_at_column()\nRETURNS TRIGGER AS $$\nBEGIN\n    NEW.updated_at = NOW();\n    RETURN NEW;\nEND;\n$$ language 'plpgsql';\n\n-- Function for updating engagement metrics\nCREATE OR REPLACE FUNCTION update_engagement_metrics()\nRETURNS TRIGGER AS $$\nBEGIN\n    IF TG_OP = 'INSERT' THEN\n        -- Update likes count when a like is added\n        IF TG_TABLE_NAME = 'post_likes' THEN\n            UPDATE post_engagement \n            SET likes_count = likes_count + 1 \n            WHERE post_id = NEW.post_id;\n        END IF;\n        RETURN NEW;\n    ELSIF TG_OP = 'DELETE' THEN\n        -- Update likes count when a like is removed\n        IF TG_TABLE_NAME = 'post_likes' THEN\n            UPDATE post_engagement \n            SET likes_count = GREATEST(0, likes_count - 1) \n            WHERE post_id = OLD.post_id;\n        END IF;\n        RETURN OLD;\n    END IF;\n    RETURN NULL;\nEND;\n$$ language 'plpgsql';\n\n-- Triggers for updated_at columns\nCREATE OR REPLACE TRIGGER update_posts_updated_at \n    BEFORE UPDATE ON posts \n    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();\n\nCREATE OR REPLACE TRIGGER update_user_profiles_updated_at \n    BEFORE UPDATE ON user_profiles \n    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();\n\n-- Triggers for engagement metrics\nCREATE OR REPLACE TRIGGER update_likes_count_insert\n    AFTER INSERT ON post_likes\n    FOR EACH ROW EXECUTE FUNCTION update_engagement_metrics();\n\nCREATE OR REPLACE TRIGGER update_likes_count_delete\n    AFTER DELETE ON post_likes\n    FOR EACH ROW EXECUTE FUNCTION update_engagement_metrics();\n\n-- ====================================\n-- DEFAULT DATA\n-- ====================================\n\n-- Insert default categories\nINSERT INTO categories (name, slug, description, color, icon, display_order, is_active) VALUES \n    ('Cloud Services', 'cloud-services', 'Articles about cloud computing platforms and services', '#3B82F6', 'cloud', 1, true),\n    ('Security', 'security', 'Cybersecurity and data protection topics', '#EF4444', 'shield', 2, true),\n    ('Technology', 'technology', 'General technology news and updates', '#10B981', 'cpu', 3, true),\n    ('Tutorials', 'tutorials', 'Step-by-step guides and how-to articles', '#F59E0B', 'book', 4, true),\n    ('DevOps', 'devops', 'DevOps practices and automation', '#8B5CF6', 'settings', 5, true),\n    ('AI & ML', 'ai-ml', 'Artificial Intelligence and Machine Learning', '#EC4899', 'brain', 6, true)\nON CONFLICT (slug) DO NOTHING;\n\n-- Insert default tags\nINSERT INTO tags (name, slug, color) VALUES\n    ('AWS', 'aws', '#FF9900'),\n    ('Azure', 'azure', '#0078D4'),\n    ('Google Cloud', 'google-cloud', '#4285F4'),\n    ('Kubernetes', 'kubernetes', '#326CE5'),\n    ('Docker', 'docker', '#2496ED'),\n    ('Security', 'security', '#EF4444'),\n    ('DevOps', 'devops', '#8B5CF6'),\n    ('Python', 'python', '#3776AB'),\n    ('JavaScript', 'javascript', '#F7DF1E'),\n    ('React', 'react', '#61DAFB'),\n    ('Node.js', 'nodejs', '#339933'),\n    ('Monitoring', 'monitoring', '#FF6B6B'),\n    ('Automation', 'automation', '#4ECDC4'),\n    ('Best Practices', 'best-practices', '#45B7D1')\nON CONFLICT (slug) DO NOTHING;