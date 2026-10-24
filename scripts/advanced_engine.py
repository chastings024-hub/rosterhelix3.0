"""Transparent, opt-in scenario modeling. No unverified medical/injury claims."""
from collections import defaultdict
from statistics import mean
from projection_engine import project

POSITIONS={'QB','RB','WR','TE'}
def opportunity(rows,season,week):
    grouped=defaultdict(list)
    for r in rows:
        if int(r['season'])==season and int(r['week'])<week and r['position'] in POSITIONS:
            grouped[r['player_id']].append(r)
    result={}
    for pid,games in grouped.items():
        games=sorted(games,key=lambda r:int(r['week']))[-5:]
        def series(key):
            vals=[]
            for r in games:
                try:
                    if r.get(key) not in ('',None):vals.append(float(r[key]))
                except (ValueError,TypeError):pass
            return round(mean(vals),2) if vals else None
        targets=series('receiving_targets');carries=series('rushing_attempts');recs=series('receptions')
        result[pid]={'games':len(games),'targets_per_game':targets,'carries_per_game':carries,'receptions_per_game':recs,
                     'opportunities_per_game':round((targets or 0)+(carries or 0),2) if targets is not None or carries is not None else None,
                     'snap_share':None,'route_participation':None,'target_share':None,
                     'note':'Targets and carries are observed; snap, route and team target share are unavailable without a separate verified feed.'}
    return result

def apply_scenario(rows,status='unknown',availability=1.0):
    """User-input what-if availability; not a medical forecast."""
    if status not in ('unknown','active','questionable','out'):raise ValueError('Invalid scenario status')
    if not 0<=availability<=1:raise ValueError('Availability must be between 0 and 1')
    output=[]
    for row in rows:
        item=dict(row)
        item['injury_status']='user scenario: '+status
        item['conditional_projection']=row['projection']
        if status=='out':item['availability_weighted_projection']=0.0
        elif row['projection'] is None:item['availability_weighted_projection']=None
        else:item['availability_weighted_projection']=round(row['projection']*availability,2)
        item['availability_assumption']=0.0 if status=='out' else availability
        output.append(item)
    return output

def rest_of_season(rows,schedule,defense,season,start_week,scoring='ppr'):
    if not 1<=start_week<=18:raise ValueError('Invalid start week')
    # Freeze player history at start_week; never use actual later results for the projections.
    baseline=project(rows,schedule,[],season,start_week,scoring)
    byid={r['id']:dict(r,weekly=[],ros_total=0.0,scheduled_games=0,missing_schedule_weeks=[]) for r in baseline}
    from projection_engine import upcoming_opponent
    from matchup_engine import matchup_factor
    schedule_weeks={int(g['week']) for g in schedule if int(g['season'])==season}
    for week in range(start_week,19):
        for pid,r in byid.items():
            opp=upcoming_opponent(schedule,season,week,r['team'])
            if opp is None:
                r['weekly'].append({'week':week,'opponent':None,'projection':None,'schedule_known':week in schedule_weeks})
                if week not in schedule_weeks:r['missing_schedule_weeks'].append(week)
                continue
            m=matchup_factor(defense,season,start_week,opp,r['position']) if defense else {'factor':1,'games':0}
            factor=float(m.get('factor',1))
            value=round(r['baseline']*factor,2)
            r['weekly'].append({'week':week,'opponent':opp,'projection':value,'matchup_factor':round(factor,3)})
            r['ros_total']+=value;r['scheduled_games']+=1
    for r in byid.values():r['ros_total']=round(r['ros_total'],2)
    return sorted(byid.values(),key=lambda r:-r['ros_total'])

def trade_sides(ros,side_a,side_b,roster_a=None,roster_b=None,starter_slots=None):
    """Starter-slot roster accounting. Explicit roster IDs and league slots required."""
    byid={p['id']:p for p in ros};roster_a=roster_a or [];roster_b=roster_b or []
    if not side_a or not side_b or set(side_a)&set(side_b):raise ValueError('Trade sides must be nonempty and distinct')
    if not set(side_a)<=set(roster_a) or not set(side_b)<=set(roster_b):raise ValueError('Outgoing players must be on the specified rosters')
    slots=starter_slots or {'QB':1,'RB':2,'WR':2,'TE':1,'FLEX':1}
    if any(int(n)<0 for n in slots.values()):raise ValueError('Invalid starter slots')
    def score(ids):
        available=[byid[x] for x in ids if x in byid]
        selected=set();total=0
        for pos in ('QB','RB','WR','TE'):
            pool=sorted((p for p in available if p['position']==pos),key=lambda p:-p['ros_total'])
            for p in pool[:int(slots.get(pos,0))]:selected.add(p['id']);total+=p['ros_total']
        flex=sorted((p for p in available if p['id'] not in selected and p['position'] in ('RB','WR','TE')),key=lambda p:-p['ros_total'])
        total+=sum(p['ros_total'] for p in flex[:int(slots.get('FLEX',0))])
        return round(total,2)
    a_before=score(roster_a);b_before=score(roster_b)
    a_after=score([x for x in roster_a if x not in side_a]+list(side_b))
    b_after=score([x for x in roster_b if x not in side_b]+list(side_a))
    return {'team_a':{'before':a_before,'after':a_after,'delta':round(a_after-a_before,2)},'team_b':{'before':b_before,'after':b_after,'delta':round(b_after-b_before,2)},'caveat':'Only selected starters, fixed baseline ROS points; excludes waivers, injuries, playoff weights and lineup constraints beyond configured slots.'}
