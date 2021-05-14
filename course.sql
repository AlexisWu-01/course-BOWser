drop table if exists course;
drop table if exists school;
drop table if exists prof;
drop table if exists taughtby;
drop table if exists userpass;
drop table if exists blog_entry;
drop table if exists movie;

create table blog_entry(
       cid integer,
       pid integer,
       entered timestamp,
       username varchar(50),
       entry text,
       primary key(cid, username,pid,entered)
);
      

create table course(
    cid integer primary key,
    department varchar(5) DEFAULT NULL,
    school_id integer,
    course_number varchar(4) default null,
    course_title varchar(100) default null
);

create table school(
       school_id integer primary key,
       school_name varchar(9)
);



create table prof(
        pid integer primary key,
        prof_name varchar(50)
);


create table taughtby(
    cid integer,
    pid integer,
    primary key(cid, pid)
);


create table userpass(
       `uid` integer primary key,
       `username` varchar(50) not null,
       `hashed` char(60),
       unique(`username`)
);


insert into prof values
(0, 'Ricarrdo Pucella'),
(1, 'Alice Paul'),
(2,'Steven Gordon');

insert into school values
 (0,'Olin'),
 (1,'Wellesley'),
 (2,'Babson');

insert into course values
(0,'ENGR',0,'3599','Web Development'),

 (1,'ENGR',1,'3531','Data Structure and Algorithms'),

 (2,'MIS',2,'3560','THE BLOCKCHAIN: BITCOIN, SMART CONTRACTS');

insert into taughtby values
(0,0),
(1,1),
(2,2);

-- insert into course (department,school_id,course_number,course_title) VALUE


