-- Verify seattleflu/schema:receiving/scan on pg

begin;

select pg_catalog.has_table_privilege('receiving.scan_set', 'select');
select pg_catalog.has_table_privilege('receiving.collection', 'select');
select pg_catalog.has_table_privilege('receiving.sample', 'select');
select pg_catalog.has_table_privilege('receiving.aliquot', 'select');

rollback;
