-- Revert seattleflu/schema:warehouse/identifier/triggers/barcode-default-from-uuid from pg

begin;

drop trigger identifier_barcode_default_from_uuid on warehouse.identifier;
drop function warehouse.identifier_barcode_default_from_uuid();

commit;
