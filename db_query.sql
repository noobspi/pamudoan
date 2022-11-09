-- get all annotated labels for all documents. good starting point
select * from labeling

-- get documents ans how many annotations
select a.documentid as docid, d.filename as docfn, count(documentid) as cnt 
from annotation a, document d
where a.documentid = d.id
group by documentid


-- get documents and how many lables
select docid, docfn, count(docid) as cnt from labeling
group by docid, docfn
order by cnt desc


-- get labels and their usage
select label, count(label) as cnt from labeling
group by label
order by cnt desc, label asc