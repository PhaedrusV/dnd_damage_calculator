from flask import Flask, render_template, request
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

@app.route('/', methods=['GET', 'POST'])
def index():
    x, y, v, w, z = 1, 8, 0, 0, 4
    advantage, disadvantage = False, False
    if request.method == 'POST':
        x = int(request.form.get('x', 0))
        y = int(request.form.get('y', 0))
        v = int(request.form.get('v', 0))
        w = int(request.form.get('w', 0))
        z = int(request.form.get('z', 0))
        advantage = 'advantage' in request.form
        disadvantage = 'disadvantage' in request.form
    return render_template('index.html', x=x, y=y, v=v, w=w, z=z, 
                          advantage=advantage, disadvantage=disadvantage)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
