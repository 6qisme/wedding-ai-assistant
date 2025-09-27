-- seed_data.sql

INSERT INTO groups (group_code, group_name, side, category, notes) VALUES
('GR001', '新郎家', 'groom', 'family', '直系親屬'),
('GR002', '新娘家', 'bride', 'family', '直系親屬'),
('GR003', '新郎朋友', 'groom', 'friend', '同學/同事'),
('GR004', '新娘朋友', 'bride', 'friend', '同學/同事'),
('GR005', '新郎親友', 'groom', 'other', '長輩帶來的'),
('GR006', '新娘親友', 'bride', 'other', '長輩帶來的')
ON CONFLICT (group_code) DO NOTHING;