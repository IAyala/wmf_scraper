select
    com.competitor_name,
    tm.task_order,
    tm.task_name,
    trm.tr_task_penalty,
    trm.tr_competition_penalty,
    trm.tr_notes
from taskmodel tm
    join taskresultmodel trm on tm.task_id = trm.task_id
    join competitionmodel cm on tm.competition_id = cm.competition_id
    join competitormodel com on com.competitor_id = trm.competitor_id
where
    cm.competition_id = 12
    and (
        trm.tr_notes like '%10.2%'
        or trm.tr_notes like '%10.3%'
    )
order by
    com.competitor_name, tm.task_order;
