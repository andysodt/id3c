-- Deploy seattleflu/schema:roles/reporter/grant-select-on-sequences to pg
-- requires: roles/reporter
-- requires: receiving/enrollment

begin;

grant select on all sequences in schema receiving, warehouse, shipping to reporter;
alter default privileges grant select on sequences to reporter;

commit;
