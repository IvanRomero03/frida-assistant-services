drop function if exists similarity_search_test2 (embedding vector (1536), tablename text);

create or replace function similarity_search_test2(embedding vector(1536), tablename text)
returns table (id uuid, metadata json, value vector(1536), similarity float)
language plpgsql
as $$
begin
    return query
    select
        test2.id, 
        test2.metadata,
        test2.vector,
        (test2.vector <#> embedding) * -1 as similarity,
    from test2
    order by test2.vector <#> embedding;
end;
$$;