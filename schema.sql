drop table if exists projects;
create table projects (
  id integer primary key autoincrement,
  title text not null,
  description text not null,
  start_time number not null,
  total_hours number not null,
  completed_hours number not null
);