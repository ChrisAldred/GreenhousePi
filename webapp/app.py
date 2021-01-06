from flask import Flask, render_template, make_response, request
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import datetime
import io
import os
import sqlite3

db = os.getenv('DB_PATH')

# Data Access
def getData(limit):
	sql = "SELECT * FROM dhtreadings ORDER BY id DESC LIMIT " + str(limit) + ";"
	dbconnect = sqlite3.connect(db)
	dbconnect.row_factory = sqlite3.Row
	cursor = dbconnect.cursor()
	cursor.execute(sql)
	rows = cursor.fetchall()
	cursor.close()
	dbconnect.commit()
	dbconnect.close()
	return rows;

# Flask Code
app = Flask(__name__)

@app.route('/plot/temp')
def plot_temp():
	rows = getData(48)
	inTemps = []
	outTemps = []
	times = []
	lux = []
	for row in rows:
		times.append(datetime.datetime.strptime(row["date"] + " " + row["time"], '%d-%b-%Y %H:%M:%S'))
		outTemps.append(row["tempOut"])
		inTemps.append(row["tempIn"])
		lux.append(row["lux"])
	ys = outTemps
	fig = Figure(figsize=[10.0, 10.0])
	axis = fig.add_subplot(2, 1, 1)
	axis.set_ylabel("Temperature [°C]")
	axis.set_xlabel("Time")
	axis.grid(True)
	xs = times
	axis.plot(xs, ys, '-b', label='Temp Out')
	axis.plot(xs, inTemps, '-r', label='Temp In')
	axis.legend();
	plt = fig.add_subplot(2, 1, 2)
	plt.set_ylabel("Lux")
	plt.set_xlabel("Time")
	plt.grid(True)
	plt.plot(xs, lux, '-b', label='Lux')
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response


@app.route('/')
def index():

	rows = getData(20)

	return render_template('page.html', rows=rows)

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port='80')