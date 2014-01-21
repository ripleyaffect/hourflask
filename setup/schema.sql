drop table if exists users;
drop table if exists projects;
create table users (
	id integer primary key autoincrement,
	username text not null,
	password text not null
);
create table projects (
  id integer primary key autoincrement,
  user_id integer not null,
  title text not null,
  description text not null,
  start_time number not null,
  total_hours number not null,
  completed_hours number not null,
  time_limit number not null
);