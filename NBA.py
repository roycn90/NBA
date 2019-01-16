import sqlite3
import pandas as pd


conn = sqlite3.connect( "data-10.sqlite" )
c = conn.cursor()

def replacePlayer(name, season,team):
    itr = c.execute('''select g.player_name, round(avg(g.eff),3), round(avg(s.salary),1)
from games g join salaries s on (g.player_name = s.player and g.season = s.season_start and g.team = s.team)
group by g.player_name
having g.eff >= (select eff from games where player_name = :name and season = :season) and s.salary <= (select avg(salary) as median
from (select salary
from salaries
where salary not null and team = :team and season_start = :season 
order by salary
limit (select case when count(salary)%2>0 then 1 else 2 end
from salaries
where salary not null and team = :team and season_start = :season )
offset (select (count(salary)+1)/2-1
from salaries
where salary not null and team = :team and season_start = :season ))) and s.positions = (select positions from salaries where player = :name and season_start = :season ) and g.team != :team and g.season >= :season-2
''', {"name": name, "season": season, "team": team}).fetchall()

    recommendation = []
    for item in itr:
        recommendation.append(item)
    return (recommendation)



def bumpSalary(name, season,team):
    itr = c.execute('''select avg(salary) from (select g.player_name,g.eff, s.salary as salary
from games g join salaries s on (g.player_name = s.player and g.season = s.season_start and g.team = s.team)
where s.salary >= 0.8*(select avg(salary) as median
from (select salary
from salaries
where salary not null and team = :team and season_start = :season
order by salary
limit (select case when count(salary)%2>0 then 1 else 2 end
from salaries
where salary not null and team = :team and season_start = :season )
offset (select (count(salary)+1)/2-1
from salaries
where salary not null and team = :team and season_start = :season ))) and g.eff >= 0.90*(select eff from games where player_name = :name and season = :season) and g.eff <=1.1*(select eff from games where player_name = :name and season = :season))''', {"name": name, "season": season, "team": team}).fetchall()

    return itr[0][0]



def findOverpaid (team,season):
    itr = c.execute('''select g.player_name, g.eff, s.salary
from games g join salaries s on (g.player_name = s.player and g.season = s.season_start and g.team = s.team)
where g.team = :team and g.season= :season and g.eff < (select avg(eff) as median
from (select eff
from games
where eff not null and team = :team and season = :season
order by eff
limit (select case when count(*)%2>0 then 1 else 2 end
from games
where eff not null and team = :team and season = :season )
offset (select (count(*)+1)/2-1
from games
where eff not null and team = :team and season = :season ))) and s.salary > (select avg(salary) as median
from (select salary
from salaries
where salary not null and team = :team and season_start = :season 
order by salary
limit (select case when count(salary)%2>0 then 1 else 2 end
from salaries
where salary not null and team = :team and season_start = :season )
offset (select (count(salary)+1)/2-1
from salaries
where salary not null and team = :team and season_start = :season )))''',{"season": season, "team": team}).fetchall()

    overpriced_players=[]
    overpriced_effs = []
    overpriced_salaries = []
    suggestions = []
    for item in itr:
        overpriced_players.append(item[0])
        overpriced_effs.append(item[1])
        overpriced_salaries.append(item[2])
    for item in overpriced_players:
        suggestions.append(replacePlayer(item, season, team))

    print(str(len(overpriced_players)) + ' overpriced players: \n')
    for i in range(len(overpriced_players)):
        print(overpriced_players[i] + ', EFF: ' + str(overpriced_effs[i]) + ', Salary: ' + str(overpriced_salaries[i]), )
        df = pd.DataFrame(suggestions[i])
        df.columns = ['Player Name', 'EFF', 'Salary']
        print('Suggested alternative players: ')
        print(df)
        print('\n')

        conn.close()


def findUnderpaid(team, season):
    itr = c.execute('''select g.player_name, s.salary
from games g join salaries s on (g.player_name = s.player and g.season = s.season_start and g.team = s.team)
where g.team = :team and g.season = :season and g.eff > (select avg(eff) as median
from (select eff
from games
where eff not null and team = :team and season = :season
order by eff
limit (select case when count(*)%2>0 then 1 else 2 end
from games
where eff not null and team = :team and season = :season)
offset (select (count(*)+1)/2-1
from games
where eff not null and team = :team and season = :season ))) and s.salary < (select avg(salary) as median
from (select salary
from salaries
where salary not null and team = :team and season_start = :season
order by salary
limit (select case when count(salary)%2>0 then 1 else 2 end
from salaries
where salary not null and team = :team and season_start = :season )
offset (select (count(salary)+1)/2-1
from salaries
where salary not null and team = :team and season_start = :season )))''', {"season": season, "team": team}).fetchall()

    print("underpaid players are: ")
    for item in itr:
        print(item[0])
        print('recommended salary: ' + str(bumpSalary(item[0], season, team)))



#print(replacePlayer('Paul Pierce', 2016, 'LAC'))
#replacePlayer('Wesley Johnson', 2016, 'LAC')

#findUnderpaid('LAC', 2016)
findOverpaid('LAC', 2016)
#findUnderpaid('CLE', 2016)


#print(bumpSalary('Matt Barnes',2012,'LAC'))
