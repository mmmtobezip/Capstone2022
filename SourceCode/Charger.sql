drop table if exists chargers;
create table chargers(
	station int,
	charger int,
	acdc int,
	interface int,
	lat double(10,5),
	lon double(10,5),
	addr varchar(200),
	primary key(station, charger)
);
	
