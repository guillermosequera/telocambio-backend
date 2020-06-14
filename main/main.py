from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Inicio - Te lo cambio"

@app.route('/productos')
def productos():
    return "Productos - Te lo cambio"

@app.route('/quienessomos')
def quienessomos():
    return "Quienes Somos - Te lo cambio"

@app.route('/contactanos')
def contactanos():
    return "<h1>Contactanos aqui</h1>"

if __name__ == '__main__':
    app.run(debug=True)
