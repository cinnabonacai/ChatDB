create table Vendor(
	id int primary key,
	name VARCHAR(255),
	year INT,
	address VARCHAR(300),
	email VARCHAR(300),
	phone_number VARCHAR(50),
	busness_type VARCHAR(25),
	country VARCHAR(20),
	website VARCHAR(2803),
	operating_time VARCHAR(60),
	is_operated BOOLEAN
);

create table Manufacturer(
	id INT primary key,
	name VARCHAR(255),
	year INT,
	address VARCHAR(300),
	email VARCHAR(300),
	phone_number VARCHAR(50),
	busness_type VARCHAR(25),
	country VARCHAR(20),
	website VARCHAR(2803),
	is_made BOOLEAN
);

create table Reviewer(
	id int primary key,
	country VARCHAR(25),
	rating DECIMAL,
	age INT,
	gender VARCHAR(25),
	phone_number VARCHAR(25),
	email VARCHAR(25),
	username VARCHAR(25),
	password VARCHAR(25),
	comment TEXT
);

create table Warehouse(
	id INT primary key,
	name VARCHAR(50),
	address VARCHAR(300),
	country VARCHAR(25),
	phone VARCHAR(25),
	email VARCHAR(25),
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

create table Product(
	id INT primary key,
	name varchar(255),
	-- Vendor_id INT(FK)
	mage varchar(2803),
	quantity INT,
	price DECIMAL,
	manufacture_id INT,
	warehouse_id INT,
	foreign key(warehouse_id) references Warehouse(id),
	reviewer_id INT,
	description TEXT,
	color VARCHAR(25),
	length DECIMAL,
	width DECIMAL,
	height DECIMAL,
	weight DECIMAL,
	material VARCHAR(25),
	origin VARCHAR(50),
	created_at DATE,
	published_at DATE,
	updated_at DATE,
	is_active BOOLEAN
);

create table Relationship_Product_Vendor(
	product_id INT,
	vendor_id INT,
	foreign key(product_id) references Product(id),
	foreign key(vendor_id) references Vendor(id),
	primary key(product_id, vendor_id)
);

create table Relationship_Product_Reviewer(
	product_id INT,
	reviewer_id INT,
	foreign key(product_id) references Product(id),
	foreign key(reviewer_id) references Reviewer(id),
	primary key(product_id, reviewer_id)
);

create table Relationship_Product_Manufacturer(
	product_id INT,
	manufacturer_id INT,
	foreign key(product_id) references Product(id),
	foreign key(manufacturer_id) references Manufacturer(id),
	primary key(product_id, manufacturer_id)
);
