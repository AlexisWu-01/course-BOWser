drop table if exists blog_entry;
drop table if exists blog_user;
create table blog_user(
    user varchar(30) primary key,
    pass varchar(30)
);

create table blog_entry(
       entered timestamp,
       user varchar(30),
       entry text,
       foreign key (user) references blog_user(user));

insert into blog_user values
 ('happy','happypass'),
 ('bashful','bashfulpass'),
 ('grumpy','grumpypass'),
 ('sleepy','sleepypass'),
 ('sneezy','sneezypass'),
 ('dopey','dopeypass'),
 ('doc','docpass'),
 ('sleazy','sleazypass'),
 ('gropey','gropeypass'),
 ('dumpy','dumpypass');

select * from blog_user;

insert into blog_entry values
 ('2020-03-24 12:34:56', 'dopey', 'First!'),
 ('2020-03-24 13:45:00', 'grumpy', 'Give it a rest, Dopey.');

select * from blog_entry;

    
