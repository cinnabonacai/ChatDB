create table Vendor_data(
	id int primary key,
	name VARCHAR(255),
	year INT,
	address VARCHAR(300),
	email VARCHAR(500),
	phone_number VARCHAR(50),
	busness_type VARCHAR(250),
	country VARCHAR(200),
	website VARCHAR(2803),
	operating_time VARCHAR(600),
	is_operated BOOLEAN
);

create table Manufacturer_data(
	id INT primary key,
	name VARCHAR(255),
	year INT,
	address VARCHAR(300),
	email VARCHAR(500),
	phone_number VARCHAR(50),
	busness_type VARCHAR(250),
	country VARCHAR(200),
	website VARCHAR(2803),
	is_made BOOLEAN
);

create table Reviewer_data(
	id int primary key,
	country VARCHAR(250),
	-- rating DECIMAL,
	age INT,
	gender VARCHAR(50),
	phone_number VARCHAR(50),
	email VARCHAR(500),
	-- comment TEXT
	introduction TEXT,
	username VARCHAR(25),
	password VARCHAR(250)
);

create table Warehouse_data(
	id INT primary key,
	name VARCHAR(50),
	address VARCHAR(300),
	country VARCHAR(250),
	phone_number VARCHAR(50),
	email VARCHAR(500),
	length DECIMAL,
	width DECIMAL,
	height DECIMAL,
	price DECIMAL,
	minimum_capacity INT,
	maximum_capacity INT,
	safety ENUM("OUTSTANDING", "GOOD", "DECENT", "POOR", "TERRIBLE"),
	humidity DECIMAL,
	temperature DECIMAL,
	is_used BOOLEAN
);

create table Product_data(
	id INT primary key,
	name varchar(255),
	-- Vendor_id INT(FK)
	image varchar(2803),
	quantity INT,
	price DECIMAL,
	-- warehouse_id INT,
	-- foreign key(warehouse_id) references Warehouse(id),
	description TEXT,
	color VARCHAR(250),
	length DECIMAL,
	width DECIMAL,
	height DECIMAL,
	weight DECIMAL,
	material VARCHAR(250),
	origin VARCHAR(500),
	created_at DATE,
	published_at DATE,
	updated_at DATE,
	is_active BOOLEAN
);

create table Relationship_Product_Vendor_data(
	product_id INT,
	vendor_id INT,
	foreign key(product_id) references Product_data(id),
	foreign key(vendor_id) references Vendor_data(id),
	primary key(product_id, vendor_id)
);

create table Relationship_Product_Reviewer_data(
	product_id INT,
	reviewer_id INT,
	comment TEXT,
	comment_time DATE,
	rating DECIMAL,
	foreign key(product_id) references Product_data(id),
	foreign key(reviewer_id) references Reviewer_data(id),
	primary key(product_id, reviewer_id)
);

create table Relationship_Product_Manufacturer_data(
	product_id INT,
	manufacturer_id INT,
	foreign key(product_id) references Product_data(id),
	foreign key(manufacturer_id) references Manufacturer_data(id),
	primary key(product_id, manufacturer_id)
);

create table Relationship_Product_Warehouse_data(
	product_id INT,
	warehouse_id INT,
	foreign key(product_id) references Product_data(id),
	foreign key(warehouse_id) references Warehouse_data(id),
	primary key(product_id, warehouse_id)
);
