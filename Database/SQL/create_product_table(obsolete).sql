create table Product(
	product_id int primary key,
	body_html varchar(2000),
	created_at date not null,
	handle varchar(100) unique,
	product_type varchar(100),
	published_at date,
	published_scope varchar(100) not null,
	status varchar(100) not null,	
	tags varchar(64000),	
	template_suffix varchar(100),
	title varchar(100) not null,
	updated_at date not null,	
	vendor varchar(100),
	-- admin_graphql_api_id varchar(2000) unique
);

create table Images(
	id int primary key,
	product_id int,
	foreign key(product_id) references  Product(id),
	created_at date not null,
	position int unique,
	src varchar(100) unique,
	width float,
	height float,
	updated_at date not null
)

create table Options(
	id varchar(20) primary key,
	product_id int,
	foreign key(product_id) references  Product(id),
	name varchar(300) not null,
	position int unique,
	values varchar(300) not null check (CHAR_LENGTH(values) <= 255),
	variants_id int,
	foreign key(variants_id) references Variants(id);
);

create table Variants(
	barcode varchar(100),
	compare_at_price float,
	created_at date not null,	
	fulfillment_service varchar(100),
	grams int,
	id varchar(20) primary key,
	image_id int unique,
	inventory_item_id unique,
	foreign key(inventory_item_id) references  InventoryItem(id),
	inventory_management varchar(100),
	inventory_policy varchar(100),
	inventory_quantity int,//An aggregate of inventory across all locations
	old_inventory_quantity int,
	position int not null,
	price float not null,
	product_id int unique,
	foreign key(product_id) references  Product(id),
	requires_shipping boolean,
	sku varchar(100) unique,
	taxable boolean,
	tax_code varchar(100),
	title varchar(100),-- The title field is a concatenation of the option1, option2, and option3 fields.
	updated_at date,
	weight float,
	weight_unit varchar(100)
	-- inventory_policy varchar(100)
);
	
create table InventoryItem(
	cost float,
	country_code_of_origin varchar(20),
	id int primary key,
	province_code_of_origin varchar(20),
	sku varchar(100) unique,
	tracked boolean,
	updated_at date,
	requires_shipping boolean
);
	
create table Country_harmonized_system_codes(
	harmonized_system_code varchar(100) primary key,
	country_code varchar(100),
	inventoryItem_id int,
	foreign key(inventoryItem_id) references  InventoryItem(id)
);

create table Location(
	active boolean,
	address1 varchar(200),
	address2 varchar(200),
	city varchar(200),
	country varchar(200),
	country_code varchar(200),
	created_at date not null,
	id int primary key,
	legacy boolean not null,
	name varchar(200),
	phone varchar(200),
	province varchar(200),
	province_code varchar(200),
	updated_at date,
	zip varchar(200),
	localized_country_name varchar(200),
	localized_province_name varchar(200)
);

create table InventoryLevel(
	available int,
	inventory_item_id int,
	foreign key(inventory_item_id) references InventoryItem(id),
	location_id int,
	foreign key(location_id) references Location(id),
	updated_at date,
	primary key (inventory_item_id, location_id)
);

create table Presentment_prices(
	variants_id int primary key,
	foreign key(variant_id) references Variants(id),
	price_currency_code varchar(10),
	price_amount float,
	compare_currency_code varchar(10),
	compare__amount float,
);

create table Images_and_variant(
	foreign key(image_id) references Images(id),
	foreign key(variant_id) references Variants(id),
	primary key (image_id, variant_id)
);
