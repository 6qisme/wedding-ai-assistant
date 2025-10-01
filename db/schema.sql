-- db/schema.sql
-- Building group sheet
CREATE TABLE IF NOT EXISTS groups(
    group_code VARCHAR(10) PRIMARY KEY,
    group_name TEXT NOT NULL,
    side VARCHAR(10) NOT NULL CHECK (side IN ('groom', 'bride')),
    category VARCHAR(20) NOT NULL CHECK (category IN ('family','friend','other')),
    notes TEXT
);

-- Building guests sheet
CREATE TABLE IF NOT EXISTS guests(
    guest_code VARCHAR(10) PRIMARY KEY,
    name TEXT,
    alias TEXT,
    seat_number INTEGER,
    attending BOOLEAN DEFAULT TRUE,
    group_code VARCHAR(10) REFERENCES groups(group_code) ON DELETE CASCADE,
    relation_role VARCHAR(20) CHECK (relation_role IN ('self','spouse','child','guest','other')),
    representative VARCHAR(10),
    display_name TEXT    
);

-- CREATE index
CREATE INDEX IF NOT EXISTS idx_guests_name ON guests(name);
CREATE INDEX IF NOT EXISTS idx_guests_alias ON guests(alias);
CREATE INDEX IF NOT EXISTS idx_guests_display_name ON guests(display_name);
CREATE INDEX IF NOT EXISTS idx_guests_group_code ON guests(group_code);
CREATE INDEX IF NOT EXISTS idx_groups_side ON groups(side);
CREATE INDEX IF NOT EXISTS idx_groups_category ON groups(category);