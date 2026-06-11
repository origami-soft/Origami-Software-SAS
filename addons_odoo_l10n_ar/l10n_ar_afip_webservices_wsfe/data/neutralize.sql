-- Revertir talonarios electrónicos a preimpresos
UPDATE document_book AS db
   SET book_type_id = preprint.id
  FROM document_book_type AS preprint
 WHERE preprint.type = 'preprint'
   AND preprint.category = db.category
   AND db.book_type_id IN (
       SELECT id FROM document_book_type WHERE type LIKE '%electronic%'
   )
   AND db.category IN ('invoice', 'refund');
