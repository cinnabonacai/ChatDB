create table Vendor(
	vendor_id int primary key,
	vendor_name VARCHAR(255),
	vendor_year INT,
	vendor_address VARCHAR(300),
	vedor_email VARCHAR(300),
	vendor_phone_number VARCHAR(50),
	vendor_busness_type VARCHAR(25),
	vendor_country VARCHAR(20),
	vendor_website VARCHAR(2803),
	vendor_operating_time VARCHAR(60),
	vendor_is_operated BOOLEAN
);

create table Manufacturer(
	manufacturer_id INT primary key,
	manufacturer_name VARCHAR(255),
	manufacturer_year INT,
	manufacturer_address VARCHAR(300),
	manufacturer_email VARCHAR(300),
	manufacturer_phone_number VARCHAR(50),
	manufacturer_business_type VARCHAR(25),
	manufacturer_country VARCHAR(20),
	manufacturer_website VARCHAR(2803),
	manufacturer_is_made BOOLEAN
);

create table Reviewer(
	reviwer_id int primary key,
	reviewer_country VARCHAR(25),
	-- rating DECIMAL,
	reviewer_age INT,
	reviewer_gender VARCHAR(25),
	reviewer_phone_number VARCHAR(25),
	reviewer_email VARCHAR(25),
	-- comment TEXT
	reviewer_introduction TEXT,
	reviewer_username VARCHAR(25),
	reviewer_password VARCHAR(25)
);

create table Warehouse(
	warehouse_id INT primary key,
	warehouse_name VARCHAR(50),
	warehouse_address VARCHAR(300),
	warehouse_country VARCHAR(25),
	warehouse_phone VARCHAR(25),
	warehouse_email VARCHAR(25),
	warehouse_length DECIMAL,
	warehouse_width DECIMAL,
	warehouse_height DECIMAL,
	warehouseprice DECIMAL,
	warehouse_minimum_capacity INT,
	warehouse_maximum_capacity INT,
	warehouse_safety ENUM("OUTSTANDING", "GOOD", "DECENT", "POOR", "TERRIBLE"),
	warehouse_humidity DECIMAL,
	warehouse_temperature DECIMAL,
	warehouse_is_used BOOLEAN
);

create table Product(
	product_id INT primary key,
	product_name varchar(255),
	-- Vendor_id INT(FK)
	product_image varchar(2803),
	product_quantity INT,
	product_price DECIMAL,
	-- manufacture_id INT,
    -- warehouse_id INT,
	-- reviewer_id INT,
	product_description TEXT,
	product_color VARCHAR(25),
	product_length DECIMAL,
	product_width DECIMAL,
	product_height DECIMAL,
	product_weight DECIMAL,
	product_material VARCHAR(25),
	product_origin VARCHAR(50),
	product_created_at DATE,
	product_published_at DATE,
	product_updated_at DATE,
	product_is_active BOOLEAN
);

create table Relationship_Product_Vendor(
	product_id INT,
	vendor_id INT,
	foreign key(product_id) references Product(product_id),
	foreign key(vendor_id) references Vendor(vendor_id),
	primary key(product_id, vendor_id)
);

create table Relationship_Product_Reviewer(
	product_id INT,
	reviewer_id INT,
	comment TEXT,
	comment_time DATE,
	rating DECIMAL,
	foreign key(product_id) references Product(product_id),
	foreign key(reviewer_id) references Reviewer(reviewer_id),
	primary key(product_id, reviewer_id)
);

create table Relationship_Product_Manufacturer(
	product_id INT,
	manufacturer_id INT,
	foreign key(product_id) references Product(product_id),
	foreign key(manufacturer_id) references Manufacturer(manufacturer_id),
	primary key(product_id, manufacturer_id)
);

create table Relationship_Product_Warehouse {
	product_id INT,
	warehouse_id INT,
	foreign key(product_id) references Product(product_id),
	foreign key(warehouse_id) references Warehouse(warehouse_id),
	primary key(product_id, warehouse_id)
}
