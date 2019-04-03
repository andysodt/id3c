-- Verify seattleflu/schema:receiving/enrollment/document-constraint on pg

begin;

insert into receiving.enrollment (document) values ('{}');

do $$ begin
    insert into receiving.enrollment (document) values ('[]');
exception
    when check_violation then
        return;
end $$;

rollback;
