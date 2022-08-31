import climateserv.api

x = 81.27
y = 29.19

GeometryCoords = [[x-.01, y+.01], [x+.01, y+.01],
                  [x+.01, y-.01], [x-.01, y-.01],
                  [x-.01, y+.01]]

DatasetType = 'CentralAsia_eMODIS'
OperationType = 'Average'
EarliestDate = '01/03/2020'
LatestDate = '03/16/2020'
SeasonalEnsemble = 'ens07'
SeasonalVariable = 'Precipitation'
Outfile = 'out.csv'

climateserv.api.request_data(DatasetType, OperationType, EarliestDate, LatestDate,
                             GeometryCoords, SeasonalEnsemble, SeasonalVariable, Outfile)
