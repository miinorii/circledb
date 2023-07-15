delete from global_lb where rank <> 1;
delete from country_lb where rank <> 1 or country_code <> 'FR';
delete from best_rank where country_code <> 'FR';
delete from score where score.id not in (select score_id from global_lb) and score.id not in (select score_id from country_lb);
vacuum "main";