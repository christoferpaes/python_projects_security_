import plotly.express as px
import pandas as pd

# Given data
data = '''2023	339,996,563	0.50%
2022	338,289,857	0.38%
2021	336,997,624	0.31%
2020	335,942,003	0.49%
2019	334,319,671	0.66%
2018	332,140,037	0.71%
2017	329,791,231	0.79%
2016	327,210,198	0.80%
2015	324,607,776	0.80%
2014	322,033,964	0.83%
2013	319,375,166	0.86%
2012	316,651,321	0.88%
2011	313,876,608	0.87%
2010	311,182,845	0.87%
2009	308,512,035	0.92%
2008	305,694,910	0.97%
2007	302,743,399	1.00%
2006	299,753,098	0.98%
2005	296,842,670	0.98%
2004	293,947,885	0.97%
2003	291,109,820	0.96%
2002	288,350,252	1.01%
2001	285,470,493	1.09%
2000	282,398,554	1.15%
1999	279,181,581	1.21%
1998	275,835,018	1.26%
1997	272,395,438	1.27%
1996	268,984,347	1.25%
1995	265,660,556	1.29%
1994	262,273,589	1.35%
1993	258,779,753	1.41%
1992	255,175,339	1.44%
1991	251,560,189	1.40%
1990	248,083,732	1.28%
1989	244,954,094	1.10%
1988	242,287,814	1.02%
1987	239,853,168	0.99%
1986	237,512,783	1.01%
1985	235,146,182	1.02%
1984	232,766,280	1.03%
1983	230,389,964	1.05%
1982	228,001,418	1.04%
1981	225,654,008	1.13%
1980	223,140,018	1.21%
1979	220,463,115	1.18%
1978	217,881,437	1.13%
1977	215,437,405	1.02%
1976	213,270,022	0.94%
1975	211,274,535	0.95%
1974	209,277,968	0.95%
1973	207,314,764	1.01%
1972	205,238,390	1.15%
1971	202,907,917	1.29%
1970	200,328,340	1.25%
1969	197,859,329	1.08%
1968	195,743,427	1.01%
1967	193,782,438	1.02%
1966	191,830,975	1.12%
1965	189,703,283	1.30%
1964	187,277,378	1.42%
1963	184,649,873	1.50%
1962	181,917,809	1.58%
1961	179,087,278	1.65%
1960	176,188,578	1.65%
1959	173,324,608	1.87%
1958	170,147,101	1.92%
1957	166,949,120	1.76%
1956	164,063,411	1.82%
1955	161,136,449	1.85%
1954	158,205,873	1.77%
1953	155,451,199	1.64%
1952	152,941,727	1.56%
1951	150,598,453	1.56%
1950	148,281,550	0.00%'''

# Splitting the data into lines
lines = data.split('\n')

# Parsing data into a dictionary
population = {}
for line in lines:
    year, population_value, _ = line.split('\t')
    population_value = int(population_value.replace(',', ''))
    year = int(year)
    population[year] = population_value

# Creating a DataFrame for plotting population over the years
df_population = pd.DataFrame(list(population.items()), columns=['Year', 'Population'])

# Calculating differences year over year
differences = {year: population[year] - population[year - 1] for year in population if year > min(population)}
df_differences = pd.DataFrame(list(differences.items()), columns=['Year', 'PopulationDifference'])

# Plotting population over the years
fig_population = px.line(df_population, x='Year', y='Population', title='US Population Over the Years')
fig_population.show()

# Plotting differences year over year
fig_differences = px.line(df_differences, x='Year', y='PopulationDifference', title='Yearly Population Differences')
fig_differences.show()

# Calculating half-decades with greatest and least growth
half_decades = [(1960, 1964), (1965, 1969), (1970, 1974), (1975, 1979), (1980, 1984),
                (1985, 1989), (1990, 1994), (1995, 1999), (2000, 2004), (2005, 2009),
                (2010, 2014), (2015, 2019), (2020, 2023)]  # Adjust for the full range of years

growth_rates = {}
for start, end in half_decades:
    growth = sum(df_differences[(df_differences['Year'] >= start) & (df_differences['Year'] <= end)]['PopulationDifference'])
    growth_rates[(start, end)] = growth

# Half-decade with greatest growth
max_growth_half_decade = max(growth_rates, key=growth_rates.get)
print("Half-decade with greatest growth:", max_growth_half_decade)

# Half-decade with least growth
min_growth_half_decade = min(growth_rates, key=growth_rates.get)
print("Half-decade with least growth:", min_growth_half_decade)

# Average growth rate for all years
average_growth = df_differences['PopulationDifference'].mean()
print("Average growth rate for all years:", average_growth)
