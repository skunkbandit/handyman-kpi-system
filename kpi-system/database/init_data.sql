-- KPI System Initial Data

-- Crawl Space Skills
INSERT INTO skills (category_id, name, display_order) VALUES
(1, 'Skirting/siding', 1),
(1, 'Wall Framing', 2),
(1, 'Joist Framing', 3),
(1, 'Insulating', 4),
(1, 'Underpinning', 5);

-- Bathroom/Kitchen/Plumbing Skills
INSERT INTO skills (category_id, name, display_order) VALUES
(2, 'Remove/Replace Faucet Assembly', 1),
(2, 'Remove/Replace Faucet Washers', 2),
(2, 'Remove/Replace Faucet Seat', 3),
(2, 'Remove/Replace Shower Faucet Cartridge', 4),
(2, 'Install Supply Lines', 5),
(2, 'Install Pex B pipe with crimp rings', 6),
(2, 'Install Pex A pipe with expansion fittings', 7),
(2, 'Install/Replace Supply Valves', 8),
(2, 'Install/Replace Bath Sink', 9),
(2, 'Remove/Replace Drain P-Trap', 10),
(2, 'Install/Replace Vanity top', 11),
(2, 'Install/Replace Vanity', 12),
(2, 'Seal Vanity corners', 13),
(2, 'Adjust Toilet', 14),
(2, 'Remove/Replace Toilet Fill Valve', 15),
(2, 'Remove/Replace Toilet Flush Valve', 16),
(2, 'Install/Replace Toilet', 17),
(2, 'Remove/Replace Tub/Shower Valve', 18),
(2, 'Install/Replace Towel Bar Kits', 19),
(2, 'Install/Replace Tub/Shower pan concrete', 20),
(2, 'Install/Replace Tub/Shower pan Fiberglass', 21),
(2, 'Install Tile Backer Board', 22),
(2, 'Install/Replace Wall Tile', 23),
(2, 'Grout Wall Tile', 24),
(2, 'Install Shower Door', 25),
(2, 'Install/Replace Disposal', 26),
(2, 'Install/Replace Kitchen Sink', 27),
(2, 'Install/Replace Hose Bibb', 28),
(2, 'Hookup Dishwasher', 29),
(2, 'Sweat Copper', 30),
(2, 'Run Gas Line', 31),
(2, 'Troubleshoot Leaks', 32),
(2, 'D.W.V. Assembly (drain waste and vent)', 33),
(2, 'Install/Replace Kitchen Cabinets', 34),
(2, 'Install/Replace/Build Countertops', 35),
(2, 'Install/Replace Cabinet Trim', 36);

-- Carpentry Exterior/Deck Skills
INSERT INTO skills (category_id, name, display_order) VALUES
(3, 'Deck Layout & Build', 1),
(3, 'Install/Replace Siding', 2),
(3, 'Install/Replace Exterior Trim', 3),
(3, 'Build Deck Railings', 4),
(3, 'Build Deck Stairs', 5),
(3, 'Roof Layout', 6),
(3, 'Replace Soffit & Fascia', 7),
(3, 'Seal with tyvek and tape', 8),
(3, 'Repair/Replace Joists & Surface', 9);

-- Carpentry Interior Skills
INSERT INTO skills (category_id, name, display_order) VALUES
(4, 'Wall Layout & Framing', 1),
(4, 'Install Molding', 2),
(4, 'Install Crown Molding', 3),
(4, 'Build Interior Stairs', 4),
(4, 'Build Cabinet boxes', 5),
(4, 'Build Cabinets doors', 6),
(4, 'Install Cabinets', 7),
(4, 'Build Laminate Countertops', 8),
(4, 'Install Wainscoting', 9);

-- Closets Skills
INSERT INTO skills (category_id, name, display_order) VALUES
(5, 'Design Layout', 1),
(5, 'Install Shelving', 2),
(5, 'Build Shoe Racks', 3),
(5, 'Build Sweater Racks', 4),
(5, 'Repair pocket door', 5),
(5, 'Install Pocket Door', 6),
(5, 'Install/repair barn door', 7);

-- Concrete Skills
INSERT INTO skills (category_id, name, display_order) VALUES
(6, 'Set Forms', 1),
(6, 'Assemble Rebar', 2),
(6, 'Sidewalk & Slab Finish', 3),
(6, 'Concrete Repair', 4),
(6, 'Lay Bricks', 5),
(6, 'Lay Cinder Blocks', 6),
(6, 'Lay Glass Block', 7),
(6, 'Expansion joint replacement', 8),
(6, 'Clean Bricks', 9);

-- Continue with Doors/Windows Skills and others in subsequent inserts...

-- Initialize Tool Categories
INSERT INTO tool_categories (name, display_order) VALUES
('General Tools', 1),
('Plumbing Tools', 2),
('Carpentry Tools', 3),
('Concrete Tools', 4),
('Drywall Tools', 5),
('Electrical Tools', 6),
('Flooring Tools', 7),
('Painting Tools', 8),
('Safety Equipment', 9);

-- General Tools
INSERT INTO tools (category_id, name, display_order) VALUES
(1, 'Hand Broom', 1),
(1, 'Chaulk Box', 2),
(1, 'Plumb Bob', 3),
(1, 'Ram Set', 4),
(1, 'Calculator', 5),
(1, 'Tape Measure', 6),
(1, 'Putty Knife', 7),
(1, '2ft Step Ladder', 8),
(1, '4ft Step Ladder', 9),
(1, '6ft Step Ladder', 10),
(1, '8ft Step Ladder', 11),
(1, 'Shop Vac', 12),
(1, '24ft Extension Ladder', 13),
(1, 'Crow Bars/Wonder Bar', 14),
(1, 'Flashlight', 15);

-- Plumbing Tools
INSERT INTO tools (category_id, name, display_order) VALUES
(2, 'Adjustable Wrenches', 1),
(2, 'Channel Locks', 2),
(2, 'Faucet Handle Puller', 3),
(2, 'Supply Line Wrench', 4),
(2, 'Tubing Cutter', 5),
(2, 'Plunger', 6),
(2, '25\' Snake', 7),
(2, 'Seat Wrench', 8),
(2, '4-Way Valve Key', 9),
(2, 'Faucet Wrench', 10),
(2, 'Closet Spud Wrench', 11),
(2, 'Strainer Locknut Wrench', 12),
(2, 'PVC Pipe Cutting Tool', 13),
(2, 'Torch Kit', 14),
(2, 'Copper Cleaning Tool', 15),
(2, 'Pipe Wrenches', 16),
(2, 'Caulk Gun', 17);

-- Carpentry Tools
INSERT INTO tools (category_id, name, display_order) VALUES
(3, 'Framing Square', 1),
(3, '2ft level', 2),
(3, '4ft Level', 3),
(3, '6ft level', 4),
(3, 'Speed Square', 5),
(3, 'Circular Saw', 6),
(3, 'Reciprocating Saw', 7),
(3, 'Compound Miter Saw', 8),
(3, 'Table Saw', 9),
(3, 'Corded 1/2" Drill', 10),
(3, 'Hammer', 11),
(3, 'Framing Nail Gun', 12),
(3, 'Finish Nail Gun', 13),
(3, 'Crown Stapler', 14),
(3, 'Air Compressor', 15),
(3, 'Nail Set', 16),
(3, 'Scribing Tool', 17),
(3, 'Finish Sander', 18),
(3, 'Cordless Drill', 19),
(3, 'Jig Saw', 20),
(3, 'Hack Saw', 21),
(3, 'Laminate Trimmer', 22),
(3, 'Laminate Roller', 23),
(3, 'Router', 24),
(3, 'Chisel set', 25),
(3, 'Allen Wrench Set', 26),
(3, 'Butt Hinge Jig', 27),
(3, 'Door Hardware Jig', 28),
(3, 'Hand Planer', 29),
(3, 'Belt Sander', 30),
(3, 'Power Planer', 31),
(3, 'Back Saw or equivalent', 32);

-- Continue with more tools in subsequent inserts...
