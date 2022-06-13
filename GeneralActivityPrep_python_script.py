import pandas as pd

df = pd.read_csv("../GeneralActivityPrepPull/data.csv", header=0)

##removing client  name columns
if 'Target Contact ::First Name' in df:
    df = df.drop('Target Contact ::First Name', 1)
if 'Target Contact ::Last Name' in df:
    df = df.drop('Target Contact ::Last Name', 1)

df.rename(columns = {'Activity Date':'Date'}, inplace = True)
df.rename(columns = {'Source Contact ::Contact Name':'Contact_Name'}, inplace = True)
df.rename(columns = {'Activity Type':'Activity_Type'}, inplace = True)

#remove check ins, first intakes and discharges, staff
selRows = df.loc[df["Activity_Type"].str.startswith('First Intake', na=False)].index
df = df.drop(selRows, axis=0)
selRows = df.loc[df["Activity_Type"].str.startswith('Check-in', na=False)].index
df = df.drop(selRows, axis=0)
selRows = df.loc[df["Activity_Type"].str.startswith('Discharged', na=False)].index
df = df.drop(selRows, axis=0)
selRows = df.loc[df["Activity_Type"].str.startswith('Staff', na=False)].index
df = df.drop(selRows, axis=0)


#moving clinicType column to end
clinicType = df.pop('Target Contact :: clinictype')
df['Target Contact :: clinictype'] = clinicType

#exploding clinicType column
df['Target Contact :: clinictype'] = df['Target Contact :: clinictype'].str.split(',')
exploded = df.explode('Target Contact :: clinictype')


#making cross tabulation report based on staff member name and clinicType
crossTab = exploded.groupby(['Contact_Name', 'Target Contact :: clinictype'])['Target Contact :: clinictype'].count().unstack().fillna(0)
crossTab['Staff_ClinicType'] = crossTab.idxmax(axis=1)
crossTab['Staff_ClinicType'] = crossTab['Staff_ClinicType'].str.lstrip()
tempPercent = (crossTab.max(axis=1)/crossTab.sum(axis=1))*100
crossTab['Highest Activity Count'] = crossTab.max(axis=1)
crossTab['Percent Total'] = tempPercent

#joining the two tables to make 
crossTabSection = crossTab.iloc[:,[-3,-1,-2]]
df = df.merge(crossTabSection, how='left', on =['Contact_Name'])

pivot = df['Activity_Type'].value_counts()

#exclusion list
exclude = pd.read_table("../GeneralActivityPrepPull/exclusionList.txt")

for index in exclude.index:
    selRows = df.loc[df["Activity_Type"].str.startswith(exclude['Exclusion List'][index], na=False)].index
    df = df.drop(selRows, axis=0)

#this is the dataframe of activities being included
pivot2 = df['Activity_Type'].value_counts()
pivot3 = pivot

for index in pivot.index:
    if index in pivot2.index:
        pivot3 = pivot3.drop(index, axis=0)

#creating list of unique staff clinicTypes
staffClinicList = df["Staff_ClinicType"].drop_duplicates()
staffClinicList = staffClinicList.dropna()


#### graph dataframes (might just do calculations here before graphing in GGPlot, easier for me)


df['Date'] = pd.to_datetime(df['Date'])
df['StaffDate'] = df['Date'].dt.to_period('M')
df['StaffDate'] = df['StaffDate'].astype(str)
#grouped = df.groupby(['Contact_Name', 'StaffDate']).size()
df['staff_activity_count'] = df.groupby(['Contact_Name', 'StaffDate']).Contact_Name.transform('count')


#m = df['Activity Date'].dt.month

### aggregate calculation test code
#df['Date'] = pd.to_datetime(df['Date'], format= '%d/%m/%y')
#y = df['Date'].dt.year
#m = df['Date'].dt.month

#df['Count_d'] = df.groupby('Date')['Date'].transform('size')
#df['Count_m'] = df.groupby([y, m])['Date'].transform('size')
#df['Count_y'] = df.groupby(y)['Date'].transform('size')
