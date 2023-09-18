a = [
    "2022 US National Championship;https://www.watchmefly.net/events/event.php?e=usnationals2022&v=tt",
    "British Nationals 2022;https://www.watchmefly.net/events/event.php?e=british2022&v=tt",
    "Open Czech National Balloon Championship 2022;https://www.watchmefly.net/events/event.php?e=czech2022&v=tt",
    "6th PRE Junior World Hot Air Balloon Championship;https://www.watchmefly.net/events/event.php?e=grudziadz2022&v=tt",
    "40. Österreichische Dopgas Heißluftballon Staatsmeisterschaft 2022;https://www.watchmefly.net/events/event.php?e=austria2022&v=tt",
    "24th FAI World Hot Air Balloon Championship 2022;https://www.watchmefly.net/events/event.php?e=worlds2022&v=tt",
    "41. Offene Österreichische Staatsmeisterschaft und 28. Steirische Landesmeisterschaft;https://www.watchmefly.net/events/event.php?e=steirische2023&v=tt",
    "Dutch Balloon Trophy 2023;https://www.watchmefly.net/events/event.php?e=dbt2023&v=tt",
    "Marijampole Cup 2023;https://www.watchmefly.net/events/event.php?e=marijampole2023&v=tt",
    "2023 BFA US National Championship;https://www.watchmefly.net/events/event.php?e=usnationals2023&v=tt",
    "36º Campeonato Brasileiro de Balonismo;https://www.watchmefly.net/events/event.php?e=cbb2023&v=tt",
    "39th Polish Hot Air Balloon Championship;https://www.watchmefly.net/events/event.php?e=poland2023&v=tt",
    "6. Horber Neckar-Balloncup and UK Nationals 2023;https://www.watchmefly.net/events/event.php?e=horberneckar2023&v=tt",
    "49e Championnat de France de Montgolfières;https://www.watchmefly.net/events/event.php?e=FRA23&v=tt",
    "32nd Enea Leszno Balloon Cup and 11th Polish Junior Championship;https://www.watchmefly.net/events/event.php?e=leszno2023&v=tt",
    "6th FAI Junior World Hot Air Balloon Championship;https://www.watchmefly.net/events/event.php?e=juniorworlds2023&v=tt",
    "Central European Cup 2023 and Pre 25th Worlds Hot Air Balloon Championship;https://www.watchmefly.net/events/event.php?e=CECUP23&v=tt",
]

result = []

for elem in a:
    result.append({"url": elem.split(";")[1], "description": elem.split(";")[0]})

print(result)
