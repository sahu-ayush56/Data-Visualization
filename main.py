from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
import plotly.express as px
import plotly
import pandas as pd
import json
app = Flask(__name__)

client = MongoClient("mongodb+srv://netclan:netclan@cluster0.btiod7t.mongodb.net/?retryWrites=true&w=majority")
db = client.Netclan
rawdata = pd.DataFrame(db.jsondata.find())
def getarray(column):
	return rawdata.drop(rawdata[(rawdata[column]=='')].index,inplace=False)[column].unique()

def plot1(df):
	data = df.drop(df[(df['sector']=='')|(df['relevance']=='')].index,inplace=False)
	fig = px.scatter(data, x="sector", y="intensity", color='likelihood', width = 1050)
	
	# fig.show()
	return fig

def plot2(df):
	data = df.drop(df[(df['region']=='') | (df['pestle']=='') | (df['region']=='world')].index,inplace=False)
	fig = px.density_heatmap(data, x="region", y="pestle", width = 1050)
	# fig.show()
	return fig

def plot3(df):
	data = df.drop(df[(df['topic']=='') | (df['country']=='') | (df['likelihood']=='')].index,inplace=False)
	data['likelihood'] = pd.to_numeric(data['likelihood'])
	fig = px.scatter(data, x="topic", y="country", color='relevance', size='likelihood', width = 1050)
	# fig.show()
	return fig

def plot4(df):
	data = df.drop(df[(df['country']=='') | (df['sector']=='')].index,inplace=False)
	co = data['country'].unique()
	co = pd.DataFrame(co, columns = ['country'])
	cnt = []
	sec = []
	for x in co['country']:
		arr = data[data['country']==x]['sector'].unique()
		cnt.append(len(arr))
		sec.append(', '.join(arr))
	co['sector_count'] = cnt
	co['sectors'] = sec
	# print(co);
	fig = px.choropleth(co, locations="country",locationmode="country names",
                    color="sector_count", # lifeExp is a column of gapminder
                    hover_name="country",hover_data=["sectors"], # column to add to hover information
                    color_continuous_scale=px.colors.sequential.Plasma, width = 1050)
	# fig.show()
	return fig

def plot5(df):
	data = df.drop(df[(df['start_year']=='')|(df['end_year']=='')].index,inplace=False)
	data = data.groupby(['start_year','end_year']).size().reset_index().rename(columns={0:'amount_of_work'})
	fig = px.scatter(data, x="start_year", y="end_year", size="amount_of_work", width = 1050)
	# fig.show()
	return fig

tags = ['end_year', 'topic', 'sector', 'region', 'pestle']
data = []
for x in tags:
	data.append(getarray(x))

@app.route('/', methods=('GET', 'POST'))
def hello():
	df = rawdata
	if request.method == "POST":
		for x in tags:
			fltr = request.form.get(x)
			if fltr!="select":
				if x=='end_year':
					df = df[df[x]==int(fltr)]
				else:	
					df = df[df[x]==fltr]
				# print(df)
				# print(fltr)	
	chart1 = json.dumps(plot1(df), cls=plotly.utils.PlotlyJSONEncoder)
	chart2 = json.dumps(plot2(df), cls=plotly.utils.PlotlyJSONEncoder)
	chart3 = json.dumps(plot3(df), cls=plotly.utils.PlotlyJSONEncoder)
	chart4 = json.dumps(plot4(df), cls=plotly.utils.PlotlyJSONEncoder)
	chart5 = json.dumps(plot5(df), cls=plotly.utils.PlotlyJSONEncoder)
	return render_template("index.html",data=data,graph1=chart1,graph2=chart2,graph3=chart3,graph4=chart4,graph5=chart5);

if __name__ == "__main__":
	app.run(debug=True)









































